"""Descarga/actualiza las fuentes de datos de la comunidad.

Uso:
    python tools/update_db.py            # actualiza todo
    python tools/update_db.py --lang     # solo textos de idioma
"""
from __future__ import annotations

import argparse
import io
import json
import sys
import tarfile
import urllib.request
from pathlib import Path

from _common import DATA, DL, ROOT  # noqa: E402  (rutas también al empaquetar)

# En Windows la consola suele ser cp1252: sin esto, imprimir una flecha
# o una tilde lanza UnicodeEncodeError y se corta la actualización.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):  # pragma: no cover
        pass

JSONMAP_URL = ("https://raw.githubusercontent.com/pljeroen/nmstoolkit/"
               "main/src/nmstoolkit/data/jsonmap.txt")
ITEMS_URL = ("https://raw.githubusercontent.com/pljeroen/nmstoolkit/"
             "main/src/nmstoolkit/data/items.json")
HANDBOOK_SHA = "142d9ffd8078944722243398202f22cbef47cd02"
HANDBOOK_TABLES = ["Crafting_Table.json", "Refining_Table.json",
                   "Substance_Table.json", "Product_Table.json",
                   "Technology_Table.json",
                   # tablas de "productos" complementarias: aportan iconos y
                   # nombres a objetos que las cinco principales no cubren
                   # (piezas de edificio, legado, corbeta, nave…)
                   "Building_Parts_Table.json", "Legacy_Item_Table.json",
                   "Corvette_Parts_Table.json", "Ship_Part_Table.json",
                   "Special_Purchase_Table.json", "Special_Rewards_Table.json",
                   "Bait_Table.json", "Fossil_Table.json", "Fish_Table.json",
                   "Purchaseable_Building_Blueprints.json"]
NPM_PKG = "assistantapps-nomanssky-info"
LANGS = ("en", "es")
# archivos de idioma que no aportan a esta herramienta
SKIP_LANG = {"SeasonalExpedition.lang.json", "AlienPuzzle.lang.json",
             "AlienPuzzleRewards.lang.json", "WeekendMissionsSeason1.lang.json",
             "WeekendMissionsSeason2.lang.json", "WeekendMissionsSeason3.lang.json"}


def fetch(url: str, dest: Path | None = None, timeout: int = 60) -> bytes:
    print(f"  ↓ {url}")
    request = urllib.request.Request(url, headers={"User-Agent": "nms-helper"})
    data = urllib.request.urlopen(request, timeout=timeout).read()
    if dest is not None:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    return data


def update_tables() -> None:
    print("Tablas de recetas (NMS-Handbook):")
    core = HANDBOOK_TABLES[:5]
    for name in HANDBOOK_TABLES:
        try:
            fetch(f"https://raw.githubusercontent.com/ApexFatality93/"
                  f"NMS-Handbook/{HANDBOOK_SHA}/JSON_Files/{name}", DL / name)
        except Exception as exc:  # noqa: BLE001
            # las tablas complementarias pueden desaparecer o cambiar de
            # nombre en un parche: no debe romper toda la actualización
            if name in core:
                raise
            print(f"  ! {name} no disponible ({exc})")
    print("IDs de objeto (nmstoolkit):")
    fetch(ITEMS_URL, DL / "items_nmstoolkit.json")
    print("Mapa de claves de los saves (nmstoolkit):")
    fetch(JSONMAP_URL, DATA / "jsonmap.txt")


def update_langs() -> None:
    print(f"Textos de {NPM_PKG} (es/en):")
    meta = json.loads(fetch(f"https://registry.npmjs.org/{NPM_PKG}"))
    version = meta["dist-tags"]["latest"]
    tarball = fetch(meta["versions"][version]["dist"]["tarball"], timeout=120)
    print(f"  versión {version}")
    archive = tarfile.open(fileobj=io.BytesIO(tarball), mode="r:gz")
    count = 0
    for member in archive.getmembers():
        parts = member.name.split("/")
        if "/assets/json/" not in member.name or not member.name.endswith(".json"):
            continue
        index = parts.index("json")
        lang = parts[index + 1]
        if lang not in LANGS or parts[-1] in SKIP_LANG:
            continue
        extracted = archive.extractfile(member)
        if extracted is None:
            continue
        dest = DL / "lang" / lang / parts[-1]
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(extracted.read())
        count += 1
    print(f"  {count} archivos de idioma")


def main() -> int:
    parser = argparse.ArgumentParser(description="Actualiza los datos del juego")
    parser.add_argument("--lang", action="store_true",
                        help="solo actualizar textos de idioma")
    parser.add_argument("--tables", action="store_true",
                        help="solo actualizar tablas de recetas")
    parser.add_argument("--no-build", action="store_true",
                        help="no reconstruir data/db.json al final")
    parser.add_argument("--icons", action="store_true",
                        help="bajar los iconos del catálogo a data/icons/ "
                             "(wiki primero, luego el proveedor de db.json)")
    parser.add_argument("--icons-force", action="store_true",
                        help="con --icons, vuelve a bajar los que ya están")
    args = parser.parse_args()

    if args.icons:
        # Los iconos no entran en db.json: se guardan aparte, en data/icons/.
        from fetch_icons import main as icons  # type: ignore
        argv = ["fetch_icons"]
        if args.icons_force:
            argv.append("--force")
        sys.argv = argv
        return icons()

    DL.mkdir(parents=True, exist_ok=True)
    try:
        if args.lang:
            update_langs()
        elif args.tables:
            update_tables()
        else:
            update_tables()
            update_langs()
    except Exception as exc:  # noqa: BLE001 - se informa al usuario
        print(f"ERROR: {exc}", file=sys.stderr)
        print("Si no hay conexión, se usarán los datos ya descargados.",
              file=sys.stderr)
        return 1

    if not args.no_build:
        print("\nReconstruyendo data/db.json ...")
        from build_db import main as build  # type: ignore
        return build()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
