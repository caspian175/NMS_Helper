"""Monta el sitio estático para GitHub Pages (python tools/build_site.py).

    web/ + data/db.json + data/glyphs/   ->   site/

site/config.js queda con `window.NMS_STATIC = true`: ahí la interfaz responde
las rutas /api/* en el navegador con data/db.json (web/static-db.js) en vez
de con el servidor Python, que es lo que hace posible publicarla en Pages.

El sitio no descarga nada: los datos son la foto versionada en el
repositorio (por eso no se rompe si se cae alguna fuente comunitaria) y los
iconos son URLs de esas bases, con el respaldo de ficha de color que ya tiene
web/app.js cuando una imagen no carga.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
DATA = ROOT / "data"


def main() -> int:
    parser = argparse.ArgumentParser(description="Monta site/ para GitHub Pages")
    parser.add_argument("--out", default=str(ROOT / "site"),
                        help="carpeta de salida (por defecto site/)")
    args = parser.parse_args()

    # --- comprobar los datos antes de montar nada ------------------------
    db_path = DATA / "db.json"
    try:
        datos = json.loads(db_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"ERROR: no se puede leer {db_path}: {exc}", file=sys.stderr)
        print("Repítela con: python tools/update_db.py", file=sys.stderr)
        return 1
    items = datos.get("items") or {}
    if len(items) < 1000:
        print(f"ERROR: solo {len(items)} objetos en {db_path}: "
              "la base no está completa.", file=sys.stderr)
        return 1
    if not datos.get("crafting") or not datos.get("refining"):
        print(f"ERROR: faltan recetas en {db_path}.", file=sys.stderr)
        return 1

    glyph_dir = DATA / "glyphs"
    glifos = sorted(glyph_dir.glob("*.png")) if glyph_dir.is_dir() else []
    if len(glifos) < 16:
        print(f"ERROR: faltan glifos de portal en {glyph_dir} "
              f"({len(glifos)}/16). Repítelos con: "
              "python tools/fetch_glyphs.py", file=sys.stderr)
        return 1

    # --- montar site/ desde cero ----------------------------------------
    destino = Path(args.out)
    if destino.exists():
        shutil.rmtree(destino)
    (destino / "data").mkdir(parents=True)
    (destino / "glyphs").mkdir()

    for fichero in sorted(WEB.iterdir()):
        if fichero.is_file():
            shutil.copy2(fichero, destino / fichero.name)
    # El indicador de modo estático es lo único que cambia respecto a web/.
    (destino / "config.js").write_text(
        "/* Generado por tools/build_site.py: la web publicada va sin "
        "servidor Python detrás; las rutas /api/* las contesta "
        "static-db.js en el navegador. */\n"
        "window.NMS_STATIC = true;\n",
        encoding="utf-8")

    shutil.copy2(db_path, destino / "data" / "db.json")
    for fichero in glifos:
        shutil.copy2(fichero, destino / "glyphs" / fichero.name)

    # Iconos que solo existen en local (data/icons/): en la web no se pueden
    # servir y se ven como ficha de color con la inicial (onerror de app.js).
    locales = sorted(
        clave for clave, objeto in items.items()
        if str((objeto or {}).get("icon") or "").startswith("/icons/"))
    if locales:
        print(f"  nota: {len(locales)} icono(s) solo en local "
              f"({', '.join(locales[:5])}): en la web se ven de color")

    ficheros = [f for f in destino.rglob("*") if f.is_file()]
    total = sum(f.stat().st_size for f in ficheros)
    print(f"site/: {len(ficheros)} ficheros, {total / 1024 / 1024:.2f} MB")
    print(f"  {len(items)} objetos · "
          f"{len(datos.get('crafting') or {})} recetas de fabricación · "
          f"{len(datos.get('refining') or [])} de refinado · "
          f"{len(glifos)} glifos")
    print("  listo para GitHub Pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
