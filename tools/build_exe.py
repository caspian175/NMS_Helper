"""Construye el ejecutable de Windows y calcula su SHA-256.

    python tools/build_exe.py

Instala PyInstaller en un entorno aparte (es una herramienta de compilación,
no una dependencia del programa) y deja el resultado en `dist/`. Al terminar
genera `dist/SHA256SUMS.txt` para que los jugadores puedan comprobar que lo
que han descargado es exactamente lo publicado.
"""
from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

from _common import ROOT

DIST = ROOT / "dist"
NAME = "NMS Helper"
VENV = Path.home() / "AppData/Local/Temp/nms_exe_build"


def hash_sha256(ruta: Path) -> str:
    digest = hashlib.sha256()
    with ruta.open("rb") as fh:
        for bloque in iter(lambda: fh.read(1 << 20), b""):
            digest.update(bloque)
    return digest.hexdigest()


def preparar_entorno() -> Path:
    """Venv con PyInstaller, para no tocar el Python del sistema."""
    python = VENV / "Scripts" / "python.exe"
    if not python.exists():
        print(f"Creando entorno de compilación en {VENV}…")
        subprocess.run([sys.executable, "-m", "venv", str(VENV)], check=True)
    print("Instalando PyInstaller y pywebview (el motor de la ventana)…")
    subprocess.run([str(python), "-m", "pip", "install", "--quiet",
                    "--disable-pip-version-check", "pyinstaller", "pywebview"],
                   check=True)
    return python


def comprimir(carpeta: Path) -> Path:
    """Zip para subir a GitHub Releases (¡sin marca de bloqueo!)."""
    destino = DIST / f"{NAME}-windows.zip"
    if destino.exists():
        destino.unlink()
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted(carpeta.rglob("*")):
            zf.write(path, Path(NAME) / path.relative_to(carpeta))
    return destino


def main() -> int:
    DIST.mkdir(exist_ok=True)
    python = preparar_entorno()
    print("Compilando (tarda un par de minutos)…")
    subprocess.run([str(python), "-m", "PyInstaller", "--noconfirm",
                    "--distpath", str(DIST), "--workpath", str(DIST / "_build"),
                    str(ROOT / "nms_helper.spec")], cwd=str(ROOT), check=True)

    carpeta = DIST / NAME
    exe = carpeta / f"{NAME}.exe"
    if not exe.exists():
        print("ERROR: no se ha generado el ejecutable", file=sys.stderr)
        return 1

    tamano = sum(p.stat().st_size for p in carpeta.rglob("*") if p.is_file())
    print(f"\nEjecutable: {exe} ({exe.stat().st_size / 1024 / 1024:.1f} MB)")
    print(f"Carpeta completa: {tamano / 1024 / 1024:.0f} MB")

    print("Comprimiendo para subir a GitHub Releases…")
    zip_path = comprimir(carpeta)
    print(f"{zip_path.name} · {zip_path.stat().st_size / 1024 / 1024:.0f} MB")

    linea_zip = f"{hash_sha256(zip_path)}  {zip_path.name}"
    linea_exe = f"{hash_sha256(exe)}  {NAME}/{exe.name}"
    (DIST / "SHA256SUMS.txt").write_text(
        linea_exe + "\n" + linea_zip + "\n", encoding="utf-8")
    print("\nSHA-256 (para publicarlo junto al ZIP):")
    print("  " + linea_zip)
    print("\nHecho. Prueba el ejecutable antes de subirlo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
