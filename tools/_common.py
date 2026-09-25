"""Rutas compartidas por las herramientas de la carpeta `tools/`.

Cuando la aplicación va empaquetada con PyInstaller, estos scripts quedan en
la carpeta de solo lectura del paquete, así que lo que hay que *escribir*
(iconos, `db.json`, caché de descargas) se resuelve en la carpeta del
ejecutable. `nms_helper.paths` ya sabe hacer esa distinción.
"""
from __future__ import annotations

import sys
from pathlib import Path

_BUNDLE = Path(__file__).resolve().parent.parent
if str(_BUNDLE) not in sys.path:
    sys.path.insert(0, str(_BUNDLE))

try:
    from nms_helper.paths import APP_DIR, CACHE_DIR, DATA_DIR, TOOLS_DIR  # type: ignore
except ImportError:  # el proyecto se está usando como código suelto
    APP_DIR = _BUNDLE
    DATA_DIR = APP_DIR / "data"
    TOOLS_DIR = Path(__file__).resolve().parent
    CACHE_DIR = TOOLS_DIR / "_dl"

ROOT = APP_DIR
DATA = DATA_DIR
DL = CACHE_DIR
ICONS_DIR = DATA_DIR / "icons"
GLYPHS_DIR = DATA_DIR / "glyphs"
DB_PATH = DATA_DIR / "db.json"
