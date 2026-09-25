"""Genera `web/nms_helper.ico` a partir del mismo diseño que `favicon.svg`.

Un `.ico` no es más que una cabecera con una lista de imágenes; desde Windows
Vista se pueden embeber PNG dentro, así que aquí se dibuja el rombo píxel a
píxel (con 4x4 de supermuestreo para que salga antialiaseado) y se guarda en
PNG puro usando solo `zlib` y `binascii`, sin ninguna dependencia.

    python tools/make_icons.py
"""
from __future__ import annotations

import binascii
import struct
import zlib
from pathlib import Path

from _common import TOOLS_DIR  # noqa: F402  (rutas también al empaquetar)

DEST = TOOLS_DIR.parent / "web" / "nms_helper.ico"
SIZES = (16, 24, 32, 48, 64, 128, 256)

# Colores del diseño (los mismos que en el CSS: --bg-2, --line, --accent)
FONDO = (15, 21, 34, 255)
BORDE = (36, 49, 73, 255)
ACENTO = (79, 209, 224, 255)
SS = 4  # supermuestreo


def _chunks(datos: bytes) -> bytes:
    """Envuelve los datos en los chunks IHDR/IDAT/IEND de un PNG."""
    out = b"\x89PNG\r\n\x1a\n"
    for tipo, cuerpo in ((b"IHDR", struct.pack(">IIBBBBB", *datos[0], 8, 6, 0, 0, 0)),
                         (b"IDAT", zlib.compress(datos[1], 9)),
                         (b"IEND", b"")):
        out += struct.pack(">I", len(cuerpo)) + tipo + cuerpo
        out += struct.pack(">I", binascii.crc32(tipo + cuerpo) & 0xFFFFFFFF)
    return out


def _dentro_redondeada(x: float, y: float, lado: float, radio: float) -> bool:
    """¿(x, y) está dentro del cuadrado redondeado de lado `lado`?"""
    cx = min(max(x, radio), lado - radio)
    cy = min(max(y, radio), lado - radio)
    return (x - cx) ** 2 + (y - cy) ** 2 <= radio * radio


def _rombo(x: float, y: float, centro: float, mitad: float) -> bool:
    return abs(x - centro) + abs(y - centro) <= mitad


def _mezclar(fondo: tuple, encima: tuple, alfa: float) -> tuple:
    return tuple(round(f * (1 - alfa) + c * alfa) for f, c in zip(fondo, encima))


def _pintar(tam: int) -> bytes:
    centro = tam / 2
    radio = tam * 0.22          # esquinas del cuadrado
    mitad_ext = tam * 0.34      # radio (L1) del rombo grande
    mitad_int = tam * 0.155     # rombo interior
    filas = bytearray()
    for py in range(tam):
        filas.append(0)        # filtro PNG "none"
        for px in range(tam):
            acum = [0.0, 0.0, 0.0, 0.0]
            for sy in range(SS):
                for sx in range(SS):
                    x = px + (sx + 0.5) / SS
                    y = py + (sy + 0.5) / SS
                    if not _dentro_redondeada(x, y, tam, radio):
                        continue          # fuera: transparente
                    # marco fino
                    borde = tam * 0.035
                    if (not _dentro_redondeada(x - borde, y - borde, tam - 2 * borde, radio)
                            or not _dentro_redondeada(x + borde, y + borde,
                                                      tam - 2 * borde, radio)):
                        color = BORDE
                    elif _rombo(x, y, centro, mitad_ext):
                        color = FONDO if _rombo(x, y, centro, mitad_int) else ACENTO
                        if _rombo(x, y, centro, mitad_int) and not _rombo(
                                x, y, centro, mitad_int * 0.72):
                            color = _mezclar(FONDO, (0, 0, 0, 255), 0.35)
                    else:
                        color = FONDO
                    for i in range(4):
                        acum[i] += color[i]
            filas.extend(round(v / (SS * SS)) for v in acum)
    return bytes(filas)


def _ico(imagenes: list[tuple[int, bytes]]) -> bytes:
    """Contenedor ICO con las imágenes ya en PNG."""
    n = len(imagenes)
    cabecera = struct.pack("<HHH", 0, 1, n)
    desplazamiento = 6 + 16 * n
    entradas, datos = b"", b""
    for tam, png in imagenes:
        entradas += struct.pack("<BBBBHHII", tam % 256, tam % 256, 0, 0, 1, 32,
                                len(png), desplazamiento)
        datos += png
        desplazamiento += len(png)
    return cabecera + entradas + datos


def main() -> int:
    imagenes = []
    for tam in SIZES:
        raw = _pintar(tam)
        imagenes.append((tam, _chunks(((tam, tam), raw))))
    DEST.write_bytes(_ico(imagenes))
    print(f"{DEST} · {len(SIZES)} tamaños · {DEST.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
