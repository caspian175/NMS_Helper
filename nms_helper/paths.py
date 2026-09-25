"""Dónde vive cada carpeta, tanto desde el código como desde el .exe.

Cuando la herramienta va empaquetada con PyInstaller, el `.exe` y la carpeta
`_internal` se colocan donde elija el usuario (una carpeta normal, no
`Program Files`), así que hay dos tipos de rutas:

* **lectura**: la interfaz (`web/`) y los scripts (`tools/`) vienen dentro del
  paquete. Se usan tal cual.
* **escritura**: la base de datos, el mapa de claves, los iconos y la caché
  van **junto al ejecutable**, para que «Actualizar datos» siga funcionando
  en una instalación normal. En la primera ejecución se copia desde el
  paquete lo que hace falta y se pueda reescribir.
"""
from __future__ import annotations

import sys
from pathlib import Path

FROZEN = bool(getattr(sys, "frozen", False))
BUNDLE_DIR = Path(getattr(sys, "_MEIPASS", "")) if FROZEN else None


def app_dir() -> Path:
    """Carpeta de la aplicación (junto al .exe, o la raíz del proyecto)."""
    if FROZEN:
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def resource(*parts: str) -> Path:
    """Ruta de algo que solo se lee: junto al .exe y, si no está, en el paquete."""
    fuera = APP_DIR.joinpath(*parts)
    if fuera.exists() or BUNDLE_DIR is None:
        return fuera
    return BUNDLE_DIR.joinpath(*parts)


def resource_dir(name: str, marker: str) -> Path:
    """Carpeta de solo lectura, buscando un fichero que la delate.

    Hace falta el marcador porque junto al ejecutable se crean carpetas
    vacías (`data/`, `tools/`) para poder escribir, y una carpeta vacía no
    debe hacer creer que el código de la aplicación está ahí.
    """
    fuera = APP_DIR / name
    if (fuera / marker).exists() or BUNDLE_DIR is None:
        return fuera
    dentro = BUNDLE_DIR / name
    return dentro if (dentro / marker).exists() else fuera


APP_DIR = app_dir()

# Lo que la aplicación puede escribir, siempre junto al ejecutable.
DATA_DIR = APP_DIR / "data"
CACHE_DIR = APP_DIR / "tools" / "_dl"
ICONS_DIR = DATA_DIR / "icons"
GLYPHS_DIR = DATA_DIR / "glyphs"
DB_PATH = DATA_DIR / "db.json"
KEYMAP_PATH = DATA_DIR / "jsonmap.txt"
ICON_MAP = ICONS_DIR / "map.json"
ICON_FILE = APP_DIR / "web" / "nms_helper.ico"

# Lo que solo se lee puede venir de dentro del paquete.
WEB_DIR = resource_dir("web", "index.html")
TOOLS_DIR = resource_dir("tools", "update_db.py")


def prepare() -> list[str]:
    """Deja la aplicación lista (solo hace trabajo en el .exe).

    Copia a la carpeta del ejecutable lo que viene dentro del paquete y que la
    aplicación necesita poder reescribir: la base de datos, el mapa de claves
    y los glifos. Devuelve avisos si algún sitio no deja escribir.
    """
    avisos: list[str] = []
    if FROZEN and BUNDLE_DIR is not None:
        import shutil
        for nombre in ("db.json", "jsonmap.txt"):
            origen = BUNDLE_DIR / "data" / nombre
            destino = DATA_DIR / nombre
            if origen.exists() and not destino.exists():
                destino.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(origen, destino)
        origen_glifos = BUNDLE_DIR / "data" / "glyphs"
        if origen_glifos.is_dir():
            GLYPHS_DIR.mkdir(parents=True, exist_ok=True)
            for png in origen_glifos.glob("*.png"):
                destino = GLYPHS_DIR / png.name
                if not destino.exists():
                    shutil.copy2(png, destino)
    for folder in (DATA_DIR, ICONS_DIR, GLYPHS_DIR, CACHE_DIR):
        try:
            folder.mkdir(parents=True, exist_ok=True)
        except OSError:
            avisos.append(f"No se puede escribir en {folder}: pon el programa "
                          f"en una carpeta donde tengas permisos.")
    return avisos


def missing_data() -> list[str]:
    """Qué falta para poder arrancar (lo comprueba run.py)."""
    falta = []
    if not DB_PATH.exists():
        falta.append("data/db.json")
    if not KEYMAP_PATH.exists():
        falta.append("data/jsonmap.txt")
    if not (WEB_DIR / "index.html").exists():
        falta.append("web/index.html")
    return falta
