"""Lector de contenedores HGPAK v2 (los `.pak` del juego desde la 5.50).

Reimplementado a partir de `monkeyman192/HGPAKtool` (MIT), sin dependencias
salvo `zstandard` para descomprimir los trozos: Python 3.12 no trae ZSTD en la
stdlib (llega en 3.14 como `compression.zstd`).

Estructura del archivo:

    0x00  "HGPAK"
    0x08  u64 version, u64 file_count, u64 chunk_count, u8 comprimido,
          7 bytes de relleno, u64 data_offset              (0x30 en total)
    0x30  índice de archivos: `file_count` entradas de 0x20 bytes
          (md5 del nombre 16 B + offset u64 + tamaño descomprimido u64).
          La entrada 0 es el manifiesto con los nombres.
    ...   índice de trozos: `chunk_count` u64 con el tamaño comprimido de cada
          trozo. El primero es el manifiesto; los datos empiezan en
          `data_offset` y cada trozo ocupa su tamaño redondeado a 0x10.

Los nombres no están en el índice (solo su md5) pero sí en el manifiesto, que es
un bloque de texto con los nombres separados por CRLF, en el mismo orden que
las entradas del índice a partir de la segunda.
"""
from __future__ import annotations

import hashlib
import pathlib
import struct
from typing import BinaryIO, Iterator, NamedTuple

CHUNK_SIZE = 0x10000          # 64 KiB descomprimidos (build de Windows)
HEADER_SIZE = 0x30
ENTRY_SIZE = 0x20
VERSION = 2


class HGPakError(Exception):
    pass


def _round16(value: int) -> int:
    return (value + 0xF) & ~0xF


def _bins(value: int, size: int = CHUNK_SIZE) -> int:
    return (value + size - 1) // size


def normalise(path: str) -> str:
    """El juego normaliza los nombres a minúsculas y con barras '/': así se
    calcula el md5 que va en el índice."""
    return pathlib.PureWindowsPath(path).as_posix().lower()


def name_hash(path: str) -> bytes:
    return hashlib.md5(normalise(path).encode()).digest()


class Entry(NamedTuple):
    hash: bytes
    offset: int        # offset en el espacio descomprimido, desde data_offset
    size: int


class HGPak:
    """Abre un .pak y da acceso a su contenido por nombre."""

    def __init__(self, path, chunk_size: int = CHUNK_SIZE):
        self.path = str(path)
        self.chunk_size = chunk_size
        self._decompressor = None
        self._fh: BinaryIO | None = None
        self.names: list[str] = []
        self.entries: list[Entry] = []
        self._chunk_offsets: list[int] = []
        self._chunk_sizes: list[int] = []
        self._open()

    # ------------------------------------------------------------- interno
    def _zstd(self):
        if self._decompressor is None:
            try:
                import zstandard
            except ModuleNotFoundError as exc:  # pragma: no cover
                raise HGPakError(
                    "hace falta zstandard para leer los .pak del juego: "
                    "pip install zstandard (o usa Python 3.14+, que trae ZSTD "
                    "en la stdlib)") from exc
            self._decompressor = zstandard.ZstdDecompressor()
        return self._decompressor

    def _decompress(self, raw: bytes) -> bytes:
        try:
            return self._zstd().decompress(raw)
        except Exception:
            # Algún trozo se guarda tal cual porque no merece la pena
            # comprimirlo.
            if len(raw) == self.chunk_size:
                return raw
            raise

    def _chunk_at(self, index: int) -> bytes:
        self._fh.seek(self._chunk_offsets[index])
        return self._decompress(self._fh.read(self._chunk_sizes[index]))

    def _open(self) -> None:
        self._fh = open(self.path, "rb")
        head = self._fh.read(HEADER_SIZE)
        if head[:5] != b"HGPAK":
            raise HGPakError(f"{self.path} no parece un HGPAK")
        version, file_count, chunk_count, compressed, data_offset = struct.unpack_from(
            "<QQQ?7xQ", head, 8)
        if version != VERSION:
            raise HGPakError(f"versión de HGPAK no soportada: {version}")
        if not compressed:
            raise HGPakError("los .pak sin comprimir no están implementados")

        self._fh.seek(HEADER_SIZE)
        raw = self._fh.read(ENTRY_SIZE * file_count)
        self.entries = [Entry(*struct.unpack_from("<16sQQ", raw, i * ENTRY_SIZE))
                        for i in range(file_count)]
        chunk_table = self._fh.read(8 * chunk_count)
        self._chunk_sizes = list(struct.unpack_from(f"<{chunk_count}Q", chunk_table))
        offset = data_offset
        for size in self._chunk_sizes:
            self._chunk_offsets.append(offset)
            offset += _round16(size)

        # El manifiesto (primera entrada) ocupa los primeros trozos.
        manifest_size = self.entries[0].size
        needed = _bins(manifest_size, self.chunk_size)
        manifest = b"".join(self._chunk_at(i) for i in range(needed))
        self.names = [name.decode("utf-8", "replace")
                      for name in manifest[:manifest_size].rstrip(b"\r\n").split(b"\r\n")]
        if len(self.names) != file_count - 1:
            raise HGPakError(
                f"manifiesto inconsistente: {len(self.names)} nombres "
                f"para {file_count - 1} entradas")

    def close(self) -> None:
        if self._fh:
            self._fh.close()
            self._fh = None

    def __enter__(self) -> "HGPak":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    # ----------------------------------------------------------------- uso
    def find(self, pattern: str = "") -> list[str]:
        needle = pattern.lower()
        return [name for name in self.names if needle in name]

    def read(self, name: str) -> bytes:
        wanted = hashlib.md5(normalise(name).encode()).digest()
        for entry in self.entries[1:]:
            if entry.hash != wanted:
                continue
            return self._read_entry(entry)
        raise KeyError(name)

    def _read_entry(self, entry: Entry) -> bytes:
        start = entry.offset
        first = start // self.chunk_size
        first_off = start % self.chunk_size
        last = (start + entry.size) // self.chunk_size
        last_off = (start + entry.size) % self.chunk_size
        if first == last:
            data = self._chunk_at(first)[first_off:first_off + entry.size]
        else:
            pieces = [self._chunk_at(first)[first_off:]]
            for index in range(first + 1, last):
                pieces.append(self._chunk_at(index))
            pieces.append(self._chunk_at(last)[:last_off] if last_off
                          else self._chunk_at(last))
            data = b"".join(pieces)
        return data[:entry.size]

    def iter_matching(self, pattern: str) -> Iterator[tuple[str, bytes]]:
        needle = pattern.lower()
        for name in self.names:
            if needle in name:
                yield name, self.read(name)
