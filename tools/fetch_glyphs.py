"""Descarga los 16 glifos de portal a `data/glyphs/`.

Los símbolos salen del decodificador de portales de la comunidad
(https://nmsportals.github.io), que es quien los dibuja al marcar una
dirección. Son los mismos 16 símbolos que aparecen en la rueda del portal del
juego; se guardan en local para que la interfaz no dependa de la red.

    python tools/fetch_glyphs.py [--force]
"""
import argparse
import urllib.request

from _common import GLYPHS_DIR  # noqa: E402  (rutas también al empaquetar)

DEST = GLYPHS_DIR
BASE = "https://nmsportals.github.io/img/glyphs"
GLYPHS = list("0123456789ABCDEF")
AGENT = {"User-Agent": "NMS-Helper/1.0 (local, personal use)"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true",
                        help="vuelve a descargar aunque ya estén")
    args = parser.parse_args()

    DEST.mkdir(parents=True, exist_ok=True)
    ok, fallos = 0, []
    for glyph in GLYPHS:
        target = DEST / f"{glyph.lower()}.png"
        if target.exists() and target.stat().st_size > 200 and not args.force:
            ok += 1
            continue
        url = f"{BASE}/{glyph.lower()}.png"
        try:
            with urllib.request.urlopen(
                    urllib.request.Request(url, headers=AGENT), timeout=30) as res:
                blob = res.read()
            if not blob.startswith(b"\x89PNG"):
                raise ValueError("la respuesta no es un PNG")
            target.write_bytes(blob)
            ok += 1
        except Exception as exc:  # noqa: BLE001
            fallos.append(f"{target.name}: {exc}")

    print(f"glifos en {DEST}: {ok}/16")
    for fallo in fallos:
        print("  FALLO", fallo)
    return 0 if not fallos else 1


if __name__ == "__main__":
    raise SystemExit(main())
