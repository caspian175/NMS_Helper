"""Servidor web local de la herramienta (solo stdlib de Python)."""
from __future__ import annotations

import json
import mimetypes
import re
import subprocess
import sys
import threading
import time
import urllib.parse
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .db import GameDB, base_id, get_db, unknown_id
from .paths import DATA_DIR, FROZEN, ICON_MAP, KEYMAP_PATH, TOOLS_DIR, WEB_DIR
from .save import SaveData, SaveError, find_saves, load_keymap, parse_save

# Qué se le pasa a tools/update_db.py (fila de la interfaz de actualización)
UPDATE_FLAGS = {"all": [], "tables": ["--tables"], "lang": ["--lang"],
                "icons": ["--icons"]}

SAVE_STEM_RE = re.compile(r"^save(\d*)$", re.IGNORECASE)


def format_address(address: dict) -> dict:
    """Dirección galáctica en el formato que comparte la comunidad.

    El save guarda coordenadas **voxel** con signo (`VoxelX/VoxelY/VoxelZ`,
    centradas en 0: X y Z entre -2048 y 2047, Y entre -128 y 127). Tanto el
    refuerzo de señal como las herramientas de la comunidad enseñan ese mismo
    dato desplazado a positivo: +2047 en X/Z y +127 en Y. Ese desplazamiento
    es el que hace falta para pasar a glifos de portal (sumando otros 2/2,
    es decir 2049 y 129, que es lo que hace nmsportals y Coordinate-Conversion).

    Resultado: `046A:0081:0D6D:0038` (X:Y:Z:índice de sistema, en hexadecimal)."""
    if not isinstance(address, dict) or not address:
        return {}
    try:
        voxel_x = int(address.get("x", 0))
        voxel_y = int(address.get("y", 0))
        voxel_z = int(address.get("z", 0))
        system = int(address.get("system", 0))
        planet = int(address.get("planet", 0))
    except (TypeError, ValueError):
        return {}
    x = (voxel_x + 2047) % 4096
    y = (voxel_y + 127) % 256
    z = (voxel_z + 2047) % 4096
    return {
        "hex": f"{x:04X}:{y:04X}:{z:04X}:{system % 65536:04X}",
        "x": x, "y": y, "z": z,
        "voxel": {"x": voxel_x, "y": voxel_y, "z": voxel_z},
        "system": system, "planet": planet,
    }


def save_pair(path: Path) -> int:
    """Agrupa los archivos de una misma partida.

    El juego escribe dos ficheros por partida (un autosave y un punto de
    restauración): save.hg + save2.hg -> partida 1, save3.hg + save4.hg ->
    partida 2, y así sucesivamente. Devuelve 0 si el nombre no sigue el
    patrón."""
    match = SAVE_STEM_RE.match(path.stem)
    if not match:
        return 0
    number = int(match.group(1) or 1)
    return (number + 1) // 2


class SnapshotStore:
    """Guarda la última lectura de cada save y solo relee si cambia."""

    def __init__(self, keymap: dict[str, str], db: GameDB):
        self.keymap = keymap
        self.db = db
        self._cache: dict[str, tuple[float, int, dict, float]] = {}
        self._lock = threading.Lock()
        self.last_error: str = ""
        self.last_read: str = ""

    def _db_mtime(self) -> float:
        try:
            return self.db.path.stat().st_mtime
        except OSError:
            return 0.0

    def invalidate(self) -> None:
        """Olvida las lecturas guardadas (la base de datos ha cambiado)."""
        with self._lock:
            self._cache.clear()

    def read(self, path: Path) -> dict:
        try:
            stat = path.stat()
        except OSError as exc:
            self.last_error = f"No se puede leer {path.name}: {exc}"
            raise SaveError(self.last_error) from exc

        # El snapshot incluye el catálogo (nombres/iconos de db.json),
        # así que hay que invalidarlo también si cambia la base de datos.
        db_mtime = self._db_mtime()
        key = str(path)
        with self._lock:
            cached = self._cache.get(key)
            if (cached and cached[0] == stat.st_mtime
                    and cached[1] == stat.st_size
                    and cached[3] == db_mtime):
                return cached[2]

        try:
            save: SaveData = parse_save(path, self.keymap)
        except SaveError as exc:
            self.last_error = str(exc)
            raise
        except Exception as exc:  # noqa: BLE001
            self.last_error = f"{path.name}: {exc}"
            raise SaveError(self.last_error) from exc

        payload = self._serialize(save)
        with self._lock:
            self._cache[key] = (stat.st_mtime, stat.st_size, payload, db_mtime)
            self.last_error = ""
            self.last_read = datetime.now().strftime("%H:%M:%S")
        return payload

    def _serialize(self, save: SaveData) -> dict:
        inventories = []
        totals: dict[str, int] = {}
        catalog: dict[str, dict] = {}

        def catalog_entry(item_id: str) -> None:
            if item_id in catalog:
                return
            item = self.db.get(item_id) or {}
            descs = item.get("desc", {}) or {}
            catalog[item_id] = {
                "names": item.get("name", {}),
                "icon": item.get("icon", ""),
                "color": item.get("color", ""),
                "symbol": item.get("symbol", ""),
                "type": item.get("type", ""),
                "class": item.get("class", ""),
                "descs": {key: (value or "")[:200]
                          for key, value in descs.items()},
            }

        for inv in save.inventories:
            slots = []
            for slot in inv.slots:
                item_id = base_id(slot.id)
                catalog_entry(item_id)
                slots.append({
                    "id": item_id,
                    "amount": slot.amount,
                    "max": slot.max_amount,
                    "x": slot.x,
                    "y": slot.y,
                    "type": slot.kind,
                    "damage": slot.damage,
                    "unknown": unknown_id(slot.id),
                })
                if slot.kind != "Technology":
                    totals[item_id] = totals.get(item_id, 0) + slot.amount
            inventories.append({
                "key": inv.key,
                "label": inv.label,
                "width": inv.width,
                "height": inv.height,
                "capacity": max(inv.capacity, len(slots)),
                "group": inv.group or "other",
                "active": inv.active,
                "slots": slots,
            })
        updated = datetime.fromtimestamp(save.mtime)
        return {
            "save": {
                "file": save.path.name,
                "profile": save.path.parent.name,
                "name": save.save_name,
                "summary": save.summary,
                "mode": save.game_mode,
                "updated": updated.strftime("%d/%m/%Y %H:%M:%S"),
                "play_time": (save.raw.get("CommonStateData") or {})
                             .get("TotalPlayTime", 0),
                "galaxy": save.galaxy,
                "address": format_address(save.address),
            },
            "wallet": {
                "units": save.units,
                "nanites": save.nanites,
                "quicksilver": save.quicksilver,
            },
            "vitals": save.vitals,
            "inventories": inventories,
            "totals": totals,
            "catalog": catalog,
            "ships": save.ships,
            "multitools": save.multi_tools,
        }


class UpdateJob:
    """Ejecuta tools/update_db.py en un hilo y guarda su salida.

    Así la interfaz puede lanzar una actualización tras un parche del juego
    y seguir leyendo el log mientras corre (no bloquea la API)."""

    MAX_LINES = 500

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._proc: subprocess.Popen | None = None
        self._lines: list[str] = []
        self.what = ""
        self.exit_code = -1

    @property
    def running(self) -> bool:
        proc = self._proc
        return proc is not None and proc.poll() is None

    def _command(self, flags: list[str]) -> list[str]:
        """Cómo lanzar la actualización.

        Desde el código es `python tools/update_db.py`. Empaquetado con
        PyInstaller no hay intérprete disponible, así que el propio
        ejecutable hace de lanzador (`NMS Helper.exe --tool update_db …`),
        que es lo que evita tener que empaquetar Python aparte.
        """
        if FROZEN:
            return [sys.executable, "--tool", "update_db", *flags]
        return [sys.executable, "update_db.py", *flags]

    def start(self, what: str) -> bool:
        """Lanza la actualización; False si ya había una en marcha."""
        with self._lock:
            if self.running:
                return False
            flags = UPDATE_FLAGS.get(what, [])
            self.what = what
            self._lines = ["$ " + " ".join(self._command(flags))]
            try:
                proc = subprocess.Popen(
                    self._command(flags),
                    cwd=str(TOOLS_DIR),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    bufsize=1,
                )
            except OSError as exc:
                self._lines.append(f"ERROR: no se pudo arrancar {exc}")
                self._proc = None
                return False
            self._proc = proc
            self.exit_code = -1
            threading.Thread(target=self._read, daemon=True).start()
            return True

    def _read(self) -> None:
        proc = self._proc
        if proc is None or proc.stdout is None:
            return
        for line in proc.stdout:
            self._append(line.rstrip("\r\n"))
        proc.wait()
        code = proc.returncode
        with self._lock:
            self.exit_code = code
        self._append("")
        if code != 0:
            self._append(f"Terminó con código {code}.")
        elif self.what == "icons":
            self._append("Hecho: iconos revisados en data/icons/.")
        else:
            self._append("Hecho: data/db.json actualizado.")

    def _append(self, line: str) -> None:
        with self._lock:
            self._lines.append(line)
            if len(self._lines) > self.MAX_LINES:
                del self._lines[:-self.MAX_LINES]

    def state(self, since: int = 0) -> dict:
        with self._lock:
            total = len(self._lines)
            start = min(max(0, since), total)
            return {
                "running": self.running,
                "what": self.what,
                "exit": self.exit_code,
                "count": total,
                "lines": self._lines[start:],
            }


class NmsServer:
    def __init__(self, db: GameDB | None = None, port: int = 8765):
        self.db = db or get_db()
        self.keymap = load_keymap(KEYMAP_PATH)
        self.store = SnapshotStore(self.keymap, self.db)
        self.updater = UpdateJob()
        self._update_was_running = False
        self._icons_mtime = 0.0
        self.port = port
        self._saves: list[Path] = []
        self._active = 0
        self._active_manual = False
        self.refresh_saves()
        self._apply_icons()

    # ------------------------------------------------------------------
    def _apply_icons(self) -> int:
        """Apunta los iconos descargados a data/icons/ (mapa id -> fichero).

        Se relee cuando cambia el mapa, así que tras `tools/fetch_icons.py`
        la interfaz los sirve sola, sin reiniciar nada.
        """
        try:
            mtime = ICON_MAP.stat().st_mtime
        except OSError:
            mtime = 0.0
        if mtime == self._icons_mtime:
            return 0
        self._icons_mtime = mtime
        raw: dict = {}
        if mtime:
            try:
                raw = json.loads(ICON_MAP.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                raw = {}
        mapping = {
            item_id: f"/icons/{entry['file']}"
            for item_id, entry in raw.items()
            if isinstance(entry, dict) and entry.get("file")
        }
        applied = self.db.set_icons(mapping)
        if applied:
            self.store.invalidate()
        return applied

    # ------------------------------------------------------------------
    def refresh_saves(self) -> list[Path]:
        self._saves = find_saves()
        if self._active >= len(self._saves):
            self._active = 0
        return self._saves

    @property
    def saves(self) -> list[Path]:
        if not self._saves:
            self.refresh_saves()
        return self._saves

    def active_save(self) -> Path | None:
        saves = self.saves
        if not saves:
            return None
        if not (0 <= self._active < len(saves)):
            self._active = 0
        # `save.hg` y `save2.hg` son la misma partida (autosave + punto de
        # restauración) y el juego va alternando entre ellos, así que, si el
        # usuario no ha elegido un archivo a mano, se sigue siempre el más
        # reciente de la pareja para no perderte ni un autoguardado.
        if not self._active_manual:
            pair = save_pair(saves[self._active])
            self._active = max(
                (i for i, p in enumerate(saves) if save_pair(p) == pair),
                key=lambda i: saves[i].stat().st_mtime,
            )
        return saves[self._active]

    def pick_newest(self) -> None:
        saves = self.saves
        if not saves:
            return
        newest = max(range(len(saves)), key=lambda i: saves[i].stat().st_mtime)
        self._active = newest

    # ------------------------------------------------------------------
    def handle_api(self, path: str, query: dict) -> tuple[int, dict | list]:
        # Un `stat` por petición: si el mapa de iconos ha cambiado (p. ej. tras
        # tools/fetch_icons.py) se aplica y se vacía la caché de snapshots.
        self._apply_icons()
        if path == "/api/status":
            saves = self.saves
            # Los saves van en pares (save.hg + save2.hg es la misma partida);
            # se agrupan para poder mostrarlos como "Partida 1", "Partida 2"…
            newest_by_pair: dict[int, float] = {}
            for p in saves:
                pair = save_pair(p)
                mtime = p.stat().st_mtime
                if mtime > newest_by_pair.get(pair, -1.0):
                    newest_by_pair[pair] = mtime
            return 200, {
                "db": {
                    "built_at": self.db.built_at,
                    "stats": self.db.stats,
                },
                "saves": [
                    {
                        "index": i,
                        "file": p.name,
                        "profile": p.parent.name,
                        "modified": datetime.fromtimestamp(
                            p.stat().st_mtime).strftime("%d/%m/%Y %H:%M"),
                        "size_kb": round(p.stat().st_size / 1024),
                        "active": i == self._active,
                        "pair": save_pair(p),
                        "newest": save_pair(p) in newest_by_pair
                                  and p.stat().st_mtime
                                  == newest_by_pair[save_pair(p)],
                    }
                    for i, p in enumerate(saves)
                ],
                "server_time": datetime.now().strftime("%H:%M:%S"),
                "last_read": self.store.last_read,
                "error": self.store.last_error,
            }

        if path == "/api/inventory":
            save = self.active_save()
            if save is None:
                return 404, {"error": "No se ha encontrado ninguna partida"}
            try:
                payload = self.store.read(save)
            except SaveError as exc:
                return 500, {"error": str(exc)}
            return 200, payload

        if path == "/api/search":
            query_text = (query.get("q") or [""])[0]
            return 200, {"results": self.db.search(query_text)}

        if path.startswith("/api/item/"):
            item_id = urllib.parse.unquote(path.split("/api/item/", 1)[1])
            detail = self.db.detail(item_id)
            # se responde aunque falte el nombre: así se pueden mostrar el
            # icono y la clase de los módulos cuya traducción sigue sin
            # resolverse en las bases comunitarias
            if not detail.get("names") and not detail.get("icon"):
                return 404, {"error": f"Objeto desconocido: {item_id}"}
            return 200, detail

        if path == "/api/select":
            index = int((query.get("i") or ["0"])[0])
            if 0 <= index < len(self.saves):
                self._active = index
                # elegido a mano: ya no se sigue el más reciente de la pareja
                self._active_manual = True
                self.store.last_error = ""
            return 200, {"active": self._active}

        if path == "/api/rescan":
            self.refresh_saves()
            self._active_manual = False
            self.pick_newest()
            return self.handle_api("/api/status", query)

        if path == "/api/update/start":
            what = (query.get("what") or ["all"])[0]
            if what not in UPDATE_FLAGS:
                what = "all"
            started = self.updater.start(what)
            return (200 if started else 409, {
                "started": started,
                "what": what,
                "error": "" if started else "Ya hay una actualización en marcha",
            })

        if path == "/api/update/state":
            try:
                since = int((query.get("since") or ["0"])[0])
            except ValueError:
                since = 0
            state = self.updater.state(max(0, since))
            # Al terminar, data/jsonmap.txt puede haber cambiado: se recarga
            # y se vacía la caché de snapshots para releer con las claves nuevas.
            if self._update_was_running and not state["running"]:
                self.keymap = load_keymap(KEYMAP_PATH)
                self.store.keymap = self.keymap
                self.store.invalidate()
            self._update_was_running = state["running"]
            return 200, state

        if path == "/api/craftable":
            kind = (query.get("kind") or ["craft"])[0]
            if kind not in ("craft", "refine"):
                kind = "craft"
            totals = self._totals()
            if totals is None:
                return 404, {"error": "No se ha encontrado ninguna partida"}
            return 200, {"kind": kind,
                         "results": self.db.craftable(totals, kind)}

        if path.startswith("/api/plan/"):
            item_id = urllib.parse.unquote(path.split("/api/plan/", 1)[1])
            try:
                qty = int((query.get("n") or ["1"])[0] or 1)
            except ValueError:
                qty = 1
            totals = self._totals()
            if totals is None:
                return 404, {"error": "No se ha encontrado ninguna partida"}
            return 200, self.db.plan(item_id, qty, totals)

        return 404, {"error": f"Ruta desconocida: {path}"}

    def _totals(self) -> dict | None:
        """Materiales del inventario de la partida activa."""
        save = self.active_save()
        if save is None:
            return None
        return self.store.read(save).get("totals", {})


def make_handler(server: NmsServer):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):  # noqa: N802
            pass

        def _send_json(self, status: int, payload) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _send_file(self, file_path: Path) -> None:
            if not file_path.exists() or not file_path.is_file():
                self._send_json(404, {"error": "no encontrado"})
                return
            body = file_path.read_bytes()
            mime, _ = mimetypes.guess_type(str(file_path))
            if mime is None:   # la stdlib no conoce los .webp de la wiki
                mime = {".webp": "image/webp", ".avif": "image/avif"}.get(
                    file_path.suffix.lower())
            self.send_response(200)
            self.send_header("Content-Type",
                             mime or "application/octet-stream")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):  # noqa: N802
            parsed = urllib.parse.urlsplit(self.path)
            path = parsed.path
            query = urllib.parse.parse_qs(parsed.query)
            if path.startswith("/api/"):
                try:
                    status, payload = server.handle_api(path, query)
                except Exception as exc:  # noqa: BLE001
                    status, payload = 500, {"error": str(exc)}
                self._send_json(status, payload)
                return
            if path == "/":
                path = "/index.html"
            prefix = next((p for p in ("/icons/", "/glyphs/") if path.startswith(p)), None)
            if prefix:
                root = (DATA_DIR / prefix.strip("/")).resolve()
                target = (root / path[len(prefix):].lstrip("/")).resolve()
                if not str(target).startswith(str(root)):
                    self._send_json(403, {"error": "prohibido"})
                    return
                self._send_file(target)
                return
            target = (WEB_DIR / path.lstrip("/")).resolve()
            if not str(target).startswith(str(WEB_DIR.resolve())):
                self._send_json(403, {"error": "prohibido"})
                return
            self._send_file(target)

    return Handler


def start_server(port: int = 8765) -> tuple[NmsServer, ThreadingHTTPServer]:
    """Levanta el servidor local y devuelve (datos, httpd) sin bloquear.

    Así `run.py` puede arrancar el servidor en un hilo y abrir la ventana de
    la aplicación, en lugar de dejar que el servidor abra el navegador.
    """
    server = NmsServer(port=port)
    server.pick_newest()
    httpd = ThreadingHTTPServer(("127.0.0.1", port), make_handler(server))
    return server, httpd


def serve(port: int = 8765, open_browser: bool = True) -> None:
    server, httpd = start_server(port)
    url = f"http://127.0.0.1:{port}"
    print(f"NMS Helper escuchando en {url}")
    if open_browser:
        import webbrowser
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        httpd.server_close()
