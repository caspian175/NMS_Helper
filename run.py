#!/usr/bin/env python3
"""NMS Helper — punto de entrada.

    python run.py                 # ventana de aplicación (o navegador si no hay pywebview)
    python run.py --browser       # fuerza el navegador
    python run.py --port 9000
    python run.py --no-browser    # no abrir nada, solo el servidor

Empaquetado con PyInstaller el mismo ejecutable hace también de lanzador de
las herramientas, que es lo que permite que «Actualizar datos» funcione sin
tener Python instalado:

    NMS Helper.exe --tool update_db --icons
"""
from __future__ import annotations

import argparse
import sys
import threading
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from nms_helper import window  # noqa: E402
from nms_helper.paths import FROZEN, TOOLS_DIR, missing_data, prepare  # noqa: E402
from nms_helper.server import start_server  # noqa: E402


class _Eco:
    """Manda la salida a la consola y, si está empaquetado, también a un log.

    En el .exe no hay consola (parece una app de verdad), así que cualquier
    mensaje se guarda en `nms_helper.log` al lado del ejecutable.
    """

    def __init__(self, ruta: Path | None) -> None:
        self.ruta = ruta
        self.archivo = None
        self.previo = None

    def __enter__(self) -> "_Eco":
        if self.ruta:
            try:
                self.archivo = self.ruta.open("a", encoding="utf-8")
            except OSError:
                self.archivo = None
        self.previo = sys.stdout
        sys.stdout = self
        return self

    def write(self, texto: str) -> int:
        if self.previo is not None:      # sin consola, previo es None
            try:
                self.previo.write(texto)
            except (OSError, ValueError):
                pass
        if self.archivo:
            try:
                self.archivo.write(texto)
                self.archivo.flush()
            except (OSError, ValueError):
                pass
        return len(texto)

    def flush(self) -> None:
        if self.previo is not None:
            try:
                self.previo.flush()
            except (OSError, ValueError):
                pass
        if self.archivo:
            try:
                self.archivo.flush()
            except (OSError, ValueError):
                pass

    def __exit__(self, *exc) -> None:
        sys.stdout = self.previo
        if self.archivo:
            self.archivo.close()
            self.archivo = None


def avisar(mensaje: str, titulo: str = "NMS Helper") -> None:
    """Mensaje en una ventana cuando no hay consola (modo .exe)."""
    if FROZEN:
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, mensaje, titulo, 0x10)
            return
        except Exception:  # noqa: BLE001
            pass
    print(mensaje)


def ejecutar_herramienta(nombre: str, argumentos: list[str]) -> int:
    """Modo lanzador: `NMS Helper --tool update_db --lang`."""
    sys.path.insert(0, str(TOOLS_DIR))
    import importlib
    log = Path(sys.executable).with_name("nms_helper.log") if FROZEN else None
    with _Eco(log):
        try:
            modulo = importlib.import_module(nombre)
        except ImportError as exc:
            print(f"ERROR: no encuentro la herramienta {nombre}: {exc}")
            return 2
        sys.argv = [nombre] + argumentos
        return int(modulo.main() or 0)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Helper local de No Man's Sky", add_help=True)
    parser.add_argument("--port", type=int, default=8765,
                        help="puerto del servidor local (por defecto 8765)")
    parser.add_argument("--browser", action="store_true",
                        help="abrir en el navegador aunque haya pywebview")
    parser.add_argument("--no-browser", action="store_true",
                        help="no abrir nada, solo dejar el servidor escuchando")
    parser.add_argument("--tool", metavar="NOMBRE",
                        help="ejecuta una herramienta de tools/ y termina")
    args, resto = parser.parse_known_args()

    if args.tool:
        return ejecutar_herramienta(args.tool, resto)

    log = Path(sys.executable).with_name("nms_helper.log") if FROZEN else None
    with _Eco(log):
        for aviso in prepare():
            print(aviso)
        falta = missing_data()
        if falta:
            avisar("Falta por preparar:\n\n  " + "\n  ".join(falta) +
                   "\n\nSi acabas de instalar el programa, ejecuta una vez:\n\n"
                   "    python tools/update_db.py")
            return 1

        try:
            server, httpd = start_server(port=args.port)
        except OSError as exc:
            # Lo más normal es que el puerto ya esté pillado por otra cosa.
            avisar(f"No se ha podido abrir el puerto {args.port}.\n\n{exc}\n\n"
                   f"Prueba con otro:\n\n"
                   f"    {'NMS Helper.exe' if FROZEN else 'python run.py'} "
                   f"--port 9000")
            return 1
        hilo = threading.Thread(target=httpd.serve_forever, daemon=True)
        hilo.start()
        url = f"http://127.0.0.1:{args.port}"
        print(f"NMS Helper escuchando en {url}")
        if log:
            print(f"Log: {log}")

        def apagar() -> None:
            httpd.shutdown()
            httpd.server_close()

        try:
            if args.no_browser:
                print("Ctrl+C para salir.")
                while True:
                    time.sleep(1)
            elif args.browser or not window.disponible():
                if not args.browser:
                    motivo = window.motivo()
                    print(f"Se abrirá en el navegador ({motivo}).")
                webbrowser.open(url)
                print("Ctrl+C para salir.")
                while True:
                    time.sleep(1)
            else:
                # La ventana manda: al cerrarla, el programa termina.
                window.abrir(url)
        except KeyboardInterrupt:
            pass
        finally:
            apagar()
            print("Servidor detenido.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
