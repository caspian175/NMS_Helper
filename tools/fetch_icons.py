"""Descarga los iconos de todo el catálogo a `data/icons/`.

Preferencia: **la wiki de No Man's Sky** (la imagen de la ficha del objeto,
que su CDN sirve en WebP y pesa ~12 KB) y, cuando la wiki no tiene ese
objeto, el proveedor que ya venga en `data/db.json` (NMS-Handbook, que trae
los PNG de 1024 px del juego, o Assistant). Todo se guarda en local: así la
interfaz funciona sin red y no sufre el bloqueo por hotlinks del CDN de la
wiki, que era el motivo de dejar la wiki para el final.

    python tools/fetch_icons.py                  # todo el catálogo
    python tools/fetch_icons.py --resolve-only   # solo mide la cobertura
    python tools/fetch_icons.py --limit 200      # una muestra
    python tools/fetch_icons.py --force          # vuelve a bajar lo que hay
    python tools/fetch_icons.py --no-wiki        # solo db.json
    python tools/fetch_icons.py --search         # busca en la wiki los que
                                                 # no tienen página exacta
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from _common import DATA_DIR, TOOLS_DIR  # noqa: E402

ROOT = TOOLS_DIR.parent
DB_PATH = DATA_DIR / "db.json"
ICONS_DIR = DATA_DIR / "icons"   # desde _common: funciona también empaquetado
MAP_PATH = ICONS_DIR / "map.json"
WIKI_CACHE = TOOLS_DIR / "_dl" / "wiki_icons.json"
WIKI_API = "https://nomanssky.fandom.com/api.php"
HEADERS = {"User-Agent": "nms-helper/1.0 (iconos del catálogo)"}
BATCH = 40              # títulos o ficheros por llamada a la API
MAGIC = ((b"\x89PNG", ".png"), (b"RIFF", ".webp"), (b"\xff\xd8\xff", ".jpg"))
SAFE = re.compile(r"[^A-Za-z0-9_-]")


# ------------------------------------------------------------------- utility
def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (text or "").lower())


def chunks(items, size):
    for start in range(0, len(items), size):
        yield items[start:start + size]


def safe_name(item_id: str) -> str:
    clean = SAFE.sub("_", item_id)
    if clean != item_id:   # evita colisiones al limpiar
        clean += "-" + hashlib.sha1(item_id.encode()).hexdigest()[:8]
    return clean


def wiki_get(params: dict) -> dict:
    url = f"{WIKI_API}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.loads(response.read().decode("utf-8"))


def load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


# ------------------------------------------------- resolución de la wiki
def image_name(wikitext: str) -> str:
    """'| image = ...' de la ficha -> nombre del fichero."""
    match = re.search(r"\|\s*image\s*=\s*([^\n|]+)", wikitext, re.IGNORECASE)
    if not match:
        return ""
    value = match.group(1).strip()
    inner = re.search(r"\[\[[Ff]ile:([^\]|]+)", value)
    name = (inner.group(1) if inner else value).strip()
    name = re.sub(r"^File:", "", name, flags=re.IGNORECASE).strip()
    if not name or name.lower() in ("none", "-", "noimage"):
        return ""
    return name


def page_images(titles: list[str]) -> dict[str, str]:
    """Título -> nombre de fichero, en lotes de `BATCH`."""
    found = {}
    for block in chunks(titles, BATCH):
        try:
            data = wiki_get({"action": "query", "prop": "revisions",
                             "rvprop": "content", "rvslots": "main", "format": "json",
                             "titles": "|".join(block)})
        except Exception as exc:  # noqa: BLE001
            print(f"  aviso: lote de la wiki falló ({exc})", file=sys.stderr)
            continue
        for page in data.get("query", {}).get("pages", {}).values():
            if "missing" in page:
                continue
            try:
                text = page["revisions"][0]["slots"]["main"]["*"]
            except (KeyError, IndexError, TypeError):
                continue
            name = image_name(text)
            if name:
                found[page.get("title", "")] = name
        time.sleep(0.1)
    return found


def file_urls(names: list[str]) -> dict[str, str]:
    """Nombre de fichero -> URL en el CDN, en lotes."""
    urls = {}
    unique = sorted(set(names))
    for block in chunks(unique, BATCH):
        try:
            data = wiki_get({"action": "query", "prop": "imageinfo", "iiprop": "url",
                             "format": "json",
                             "titles": "|".join(f"File:{n}" for n in block)})
        except Exception as exc:  # noqa: BLE001
            print(f"  aviso: lote de ficheros falló ({exc})", file=sys.stderr)
            continue
        for page in data.get("query", {}).get("pages", {}).values():
            info = page.get("imageinfo")
            if info and info[0].get("url"):
                urls[page.get("title", "")[5:]] = info[0]["url"]
        time.sleep(0.1)
    return urls


def search_image(title: str) -> str:
    """Respaldo: busca la página si el título exacto no existe."""
    data = wiki_get({"action": "query", "list": "search", "srsearch": title,
                     "srlimit": "5", "format": "json"})
    for hit in data.get("query", {}).get("search", []):
        if norm(hit.get("title", "")) == norm(title):
            page = wiki_get({"action": "parse", "page": hit["title"],
                             "prop": "wikitext", "format": "json", "redirects": "1"})
            text = page.get("parse", {}).get("wikitext", {}).get("*", "")
            return image_name(text)
    return ""


def resolve_wiki(items: dict, use_search: bool, refresh: bool) -> dict:
    """nombre en inglés normalizado -> URL del icono en la wiki (con caché).

    Se prueban dos vías, porque cada una cubre cosas distintas:
      1. la imagen de la ficha del objeto (|image = del wikitext);
      2. el nombre del fichero deducido del icono que ya trae db.json
         (`substance.fuel.1.png` -> `File:SUBSTANCE.FUEL.1.png`).

    Comparte fichero de caché con `tools/build_db.py`, así que lo que se
    resuelve aquí no se vuelve a preguntar al construir la base de datos.
    """
    cache = load_json(WIKI_CACHE, {})
    titles, deduced = {}, {}
    for item in items.values():
        name = ((item.get("name") or {}).get("en") or "").strip()
        if not name:
            continue
        key = norm(name)
        titles.setdefault(key, name)
        icon = (item.get("icon") or "").strip()
        if icon.startswith("http"):
            stem = re.sub(r"\.(png|dds|jpg|jpeg|webp)$", "", icon.rsplit("/", 1)[-1],
                          flags=re.IGNORECASE)
            if stem:
                deduced[key] = stem.upper() + ".png"

    pending = [name for key, name in titles.items()
               if key not in cache or (refresh and not cache[key])]
    print(f"wiki: {len(titles)} nombres, {len(pending)} por resolver "
          f"({len(cache)} ya en caché)")

    # 1) imagen de la ficha
    by_title = page_images(pending)
    wanted = [name for name in by_title.values() if name]

    # 2) nombre deducido para lo que no tiene ficha
    if not use_search:
        for key, name in titles.items():
            if name in by_title or not deduced.get(key):
                continue
            wanted.append(deduced[key])
    if use_search:
        missing = [name for name in pending if name not in by_title]
        print(f"wiki: buscando {len(missing)} páginas por nombre…")
        for name in missing:
            try:
                hit = search_image(name)
            except Exception:  # noqa: BLE001
                hit = ""
            if hit:
                by_title[name] = hit
                wanted.append(hit)
            time.sleep(0.15)

    urls = file_urls([n for n in wanted if n])
    for key, name in titles.items():
        found = urls.get(by_title.get(name, ""), "") or urls.get(deduced.get(key, ""), "")
        if found or key in cache or refresh:
            cache[key] = found
    WIKI_CACHE.parent.mkdir(parents=True, exist_ok=True)
    WIKI_CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1,
                                     sort_keys=True), encoding="utf-8")
    found_count = sum(1 for url in cache.values() if url)
    print(f"wiki: {found_count} de {len(titles)} con icono "
          f"({100 * found_count // max(1, len(titles))} %)")
    return cache


# ------------------------------------------------------------------ descarga
def provider_of(url: str) -> str:
    host = urllib.parse.urlsplit(url).netloc
    if "fandom" in host or "wikia" in host or "nocookie" in host:
        return "wiki"
    if "nmsassistant" in host:
        return "assistant"
    if "github" in host:
        return "handbook"
    return "otro"


def download(url: str, stem: str) -> tuple[str, int] | None:
    """Descarga un icono; devuelve (fichero, bytes) o None."""
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(request, timeout=45) as response:
                blob = response.read()
            for magic, extension in MAGIC:
                if blob.startswith(magic):
                    if magic == b"RIFF" and blob[8:12] != b"WEBP":
                        continue
                    target = ICONS_DIR / f"{stem}{extension}"
                    target.write_bytes(blob)
                    return target.name, len(blob)
            return None
        except Exception:  # noqa: BLE001
            if attempt < 2:
                time.sleep(0.5 * (attempt + 1))
    return None


# ---------------------------------------------------------------------- main
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--limit", type=int, default=0, help="solo N objetos")
    parser.add_argument("--force", action="store_true", help="rebaja lo que ya está")
    parser.add_argument("--no-wiki", action="store_true", help="ignora la wiki")
    parser.add_argument("--search", action="store_true",
                        help="busca en la wiki las páginas que no existen por nombre")
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--resolve-only", action="store_true",
                        help="solo mide la cobertura, no descarga")
    parser.add_argument("--refresh", action="store_true",
                        help="vuelve a preguntar a la wiki los que no encontró")
    args = parser.parse_args()

    db = load_json(DB_PATH, {})
    items = db.get("items") or {}
    if args.limit:
        items = dict(list(items.items())[:args.limit])
    print(f"objetos en db.json: {len(items)}")

    wiki = {} if args.no_wiki else resolve_wiki(items, args.search, args.refresh)
    if args.resolve_only:
        return 0

    # Plan: wiki primero, luego el proveedor de db.json.
    plan: list[tuple[str, list[tuple[str, str]]]] = []
    for item_id, item in items.items():
        candidates = []
        name = ((item.get("name") or {}).get("en") or "").strip()
        if name:
            url = wiki.get(norm(name)) or ""
            if url:
                candidates.append((url, "wiki"))
        remote = (item.get("icon") or "").strip()
        if remote.startswith("http") and not any(u == remote for u, _ in candidates):
            candidates.append((remote, provider_of(remote)))
        if candidates:
            plan.append((item_id, candidates))

    ICONS_DIR.mkdir(parents=True, exist_ok=True)
    mapa = load_json(MAP_PATH, {})
    hechos, fallidos, bytes_total = 0, 0, 0
    origenes: dict[str, int] = {}

    def process(job):
        item_id, candidates = job
        stem = safe_name(item_id)
        if not args.force:
            for extension in (".png", ".webp", ".jpg"):
                if (ICONS_DIR / f"{stem}{extension}").exists():
                    return item_id, None, 0, "ya estaba"
        for url, source in candidates:
            result = download(url, stem)
            if result:
                name, size = result
                return item_id, {"file": name, "src": source, "url": url}, size, "descargado"
            time.sleep(0.2)
        return item_id, None, 0, "sin icono"

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for index, (item_id, entry, size, status) in enumerate(pool.map(process, plan), 1):
            if entry:
                mapa[item_id] = entry
                hechos += 1
                bytes_total += size
                origenes[entry["src"]] = origenes.get(entry["src"], 0) + 1
            elif status == "sin icono":
                fallidos += 1
            if index % 250 == 0:
                print(f"  {index}/{len(plan)}…")

    MAP_PATH.write_text(json.dumps(mapa, ensure_ascii=False, indent=1, sort_keys=True),
                        encoding="utf-8")
    print(f"\niconos en el mapa: {len(mapa)} (nuevos: {hechos}, "
          f"sin icono en ninguna fuente: {fallidos})")
    for source, count in sorted(origenes.items(), key=lambda kv: -kv[1]):
        print(f"  {source:<10} {count}")
    print(f"descargados {bytes_total / 1024 / 1024:.0f} MB en data/icons/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
