# -*- mode: python ; coding: utf-8 -*-
"""Empaquetado de NMS Helper para Windows (PyInstaller).

Decisiones que importan, todas explicadas en el README:

* **onedir, no onefile**: un ejecutable de un solo archivo se descomprime en
  %TEMP% cada vez que arranca, y ese patrón (escritura en temporal + binario
  sin firmar) es el que más avisos de antivirus dispara. Una carpeta es más
  aburrida y pesa lo mismo.
* **--noupx**: los empaquetadores que comprimen el binario (UPX) son la otra
  causa clásica de detecciones por heurística.
* **Sin firmar**: mientras no haya certificado, SmartScreen avisará. Se
  publica el SHA-256 del ZIP para que cada jugador pueda comprobarlo.

Uso:  python tools/build_exe.py
(o directamente:  pyinstaller nms_helper.spec --noconfirm)
"""
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_all

ROOT = Path(SPECPATH).resolve()
ONEDIR = "NMS Helper"

# pywebview necesita sus módulos de plataforma y las DLL de pythonnet, que
# si no se declaran no llegan al paquete.
datatas, binaries, hiddenimports = [], [], []
for paquete in ("pywebview", "pythonnet", "bottle", "proxy_tools", "typing_extensions"):
    try:
        d, b, h = collect_all(paquete)
    except Exception as exc:  # noqa: BLE001 - avisa, no falla en silencio
        print(f"AVISO: no se pudo reunir {paquete}: {exc}")
        continue
    datatas += d
    binaries += b
    hiddenimports += h
hiddenimports += ["webview.platforms.winforms", "clr"]
# Las herramientas viajan como código fuente dentro del paquete, así que
# PyInstaller no las analiza: hay que declarar la stdlib que usan.
hiddenimports += [
    "urllib.request", "urllib.error", "urllib.parse", "http.client", "ssl",
    "email", "email.parser", "concurrent.futures", "hashlib", "tarfile",
    "binascii", "zlib", "argparse", "importlib", "ctypes", "ctypes.wintypes",
    "shutil", "struct", "json", "re", "unicodedata", "datetime", "mimetypes",
]

# Lo que sí se lleva dentro: la interfaz, la base de datos y las
# herramientas (el ejecutable las usa como lanzador para «Actualizar datos»).
# Importante: cada fichero va a la misma carpeta relativa que en el proyecto
# (`data/db.json` -> `data/db.json`), porque `nms_helper/paths.py` las busca
# por su nombre.
for patrón in ("web/*.html", "web/*.css", "web/*.js", "web/*.svg", "web/*.ico",
               "data/db.json", "data/jsonmap.txt", "data/glyphs/*.png",
               "tools/*.py"):
    for ruta in sorted(ROOT.glob(patrón)):
        relativo = ruta.relative_to(ROOT).as_posix()
        destino = relativo.rsplit("/", 1)[0] if "/" in relativo else "."
        datatas.append((str(ruta), destino))

# Y lo que NO: iconos (219 MB, se bajan cuando el jugador lo pida) ni la
# caché de descargas.
a = Analysis(
    [str(ROOT / "run.py")],
    pathex=[str(ROOT)],
    binaries=binaries,
    datas=datatas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter", "PyQt5", "PyQt6", "PySide2", "PySide6", "gi",
              "matplotlib", "numpy", "pandas", "scipy", "pytest", "unittest",
              "pydoc_data", "setuptools", "pip", "sqlite3", "test"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=ONEDIR,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,                      # importante: sin UPX
    console=False,                 # sin ventana de consola: es una app
    icon=str(ROOT / "web" / "nms_helper.ico"),
    version=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name=ONEDIR,
)
