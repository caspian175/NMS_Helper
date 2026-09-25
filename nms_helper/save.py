"""Lector de partidas de No Man's Sky (.hg).

Los saves son JSON comprimido en bloques LZ4 (magia 0xFEEDA1E5) con las
claves ofuscadas a 3 caracteres. Este módulo decodifica el archivo y
extrae la información que necesita la interfaz.
"""

from __future__ import annotations

import json
import struct
from dataclasses import dataclass, field
from pathlib import Path

BLOCK_MAGIC = 0xFEEDA1E5


class SaveError(Exception):
    """Error al leer o interpretar un archivo de guardado."""


# --------------------------------------------------------------------------
# LZ4 (solo el formato de bloque plano que usa el juego)
# --------------------------------------------------------------------------

def _lz4_block_decompress(src: bytes) -> bytes:
    dst = bytearray()
    i, n = 0, len(src)
    while i < n:
        token = src[i]
        i += 1
        lit_len = token >> 4
        if lit_len == 15:
            while True:
                if i >= n:
                    raise SaveError("bloque LZ4 truncado (literales)")
                b = src[i]
                i += 1
                lit_len += b
                if b != 255:
                    break
        dst += src[i:i + lit_len]
        i += lit_len
        if i >= n:
            break
        if i + 2 > n:
            raise SaveError("bloque LZ4 truncado (offset)")
        offset = src[i] | (src[i + 1] << 8)
        i += 2
        if offset == 0 or offset > len(dst):
            raise SaveError("offset de match inválido en bloque LZ4")
        match_len = token & 0xF
        if match_len == 15:
            while True:
                if i >= n:
                    raise SaveError("bloque LZ4 truncado (match)")
                b = src[i]
                i += 1
                match_len += b
                if b != 255:
                    break
        match_len += 4
        start = len(dst) - offset
        for j in range(match_len):
            dst.append(dst[start + j])
    return bytes(dst)


def decompress_save(raw: bytes) -> bytes:
    """Devuelve el JSON interior de un archivo .hg."""
    if raw[:2] == b'{"':
        return raw
    out = bytearray()
    off = 0
    total = len(raw)
    while off < total:
        if off + 16 > total:
            raise SaveError("cabecera de bloque incompleta")
        magic, comp, _decomp, _reserved = struct.unpack_from("<IIII", raw, off)
        if magic != BLOCK_MAGIC:
            raise SaveError(f"magia de bloque incorrecta en {off}: {magic:#x}")
        off += 16
        if off + comp > total:
            raise SaveError("payload de bloque incompleto")
        out += _lz4_block_decompress(raw[off:off + comp])
        off += comp
    return bytes(out)


# --------------------------------------------------------------------------
# Desofuscado de claves
# --------------------------------------------------------------------------

def load_keymap(path: Path) -> dict[str, str]:
    """Carga jsonmap.txt (pares `ofuscado<TAB>legible` por línea)."""
    mapping: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t") if "\t" in line else line.split(None, 1)
        if len(parts) != 2:
            continue
        mapping[parts[0]] = parts[1]
    if not mapping:
        raise SaveError(f"mapa de claves vacío: {path}")
    return mapping


def deobfuscate(value, mapping: dict[str, str]):
    """Sustituye recursivamente las claves ofuscadas por las legibles."""
    if isinstance(value, dict):
        return {
            mapping.get(k, k): deobfuscate(v, mapping)
            for k, v in value.items()
        }
    if isinstance(value, list):
        return [deobfuscate(v, mapping) for v in value]
    return value


# --------------------------------------------------------------------------
# Modelo de uso
# --------------------------------------------------------------------------

@dataclass
class Slot:
    id: str
    amount: int
    max_amount: int
    x: int
    y: int
    kind: str = ""          # Substance / Product / Technology...
    damage: float = 0.0     # solo tecnologías
    special: str = ""       # TechBonus, Fuel, Ammo...


@dataclass
class Inventory:
    key: str
    label: str
    width: int = 0
    height: int = 0
    slots: list[Slot] = field(default_factory=list)
    group: str = ""      # suit / ship / freighter / multitool / storage…
    active: bool = False  # contenedor en uso (nave o multiherramienta actual)
    capacity: int = 0    # huecos reales (ValidSlotIndices)


@dataclass
class SaveData:
    path: Path
    mtime: float
    size: int
    save_name: str = ""
    summary: str = ""
    game_mode: str = ""
    timestamp: int = 0
    units: int = 0
    nanites: int = 0
    quicksilver: int = 0
    vitals: dict = field(default_factory=dict)
    inventories: list[Inventory] = field(default_factory=list)
    ships: list[dict] = field(default_factory=list)
    multi_tools: list[dict] = field(default_factory=list)
    galaxy: int = 0
    address: dict = field(default_factory=dict)
    raw: dict = field(default_factory=dict)


# Inventario -> etiqueta que se muestra en la interfaz
# El juego solo tiene dos pestañas por contenedor (inventario y tecnología);
# "Carga" es un residuo de versiones antiguas y normalmente viene vacío, así
# que solo se muestra si la partida guarda algo ahí.
INVENTORY_LABELS = {
    "Inventory": "Exotraje · Inventario",
    "Inventory_Cargo": "Exotraje · Carga (legado)",
    "Inventory_TechOnly": "Exotraje · Tecnología",
}

# Contenedores y cajas sueltas que interesan al jugador
_EXTRA_INVENTORIES = {
    "Chest1Inventory": "Contenedor de refugio 1",
    "Chest2Inventory": "Contenedor de refugio 2",
    "Chest3Inventory": "Contenedor de refugio 3",
    "Chest4Inventory": "Contenedor de refugio 4",
    "Chest5Inventory": "Contenedor de refugio 5",
    "Chest6Inventory": "Contenedor de refugio 6",
    "Chest7Inventory": "Contenedor de refugio 7",
    "Chest8Inventory": "Contenedor de refugio 8",
    "Chest9Inventory": "Contenedor de refugio 9",
    "Chest10Inventory": "Contenedor de refugio 10",
    "ChestMagicInventory": "Contenedor de exóticos",
    "ChestMagic2Inventory": "Contenedor de exóticos 2",
    "RocketLockerInventory": "Cohetes del exotraje",
    "CookingIngredientsInventory": "Ingredientes (nutrientes)",
    "FoodUnitInventory": "Procesador de nutrientes",
    "FishPlatformInventory": "Plataforma de pesca",
    # "CorvetteStorageInventory" (taller de corbetas) queda fuera a petición:
    # no aporta nada a esta herramienta.
}

_FREIGHTER_LABELS = {
    "FreighterInventory": "Carguero · Inventario",
    "FreighterInventory_Cargo": "Carguero · Carga (legado)",
    "FreighterInventory_TechOnly": "Carguero · Tecnología",
}

GAME_MODES = {
    1: "Supervivencia", 2: "Permanencia", 3: "Normal", 4: "Extremo",
    5: "Relámpago", 6: "Expedición", 7: "Constructor", 8: "Odissea",
}


def _slot_from_entry(entry: dict) -> Slot | None:
    idx = entry.get("Index") or {}
    tech = entry.get("Technology") or {}
    return Slot(
        id=entry.get("Id", ""),
        amount=int(entry.get("Amount", 0) or 0),
        max_amount=int(entry.get("MaxAmount", 0) or 0),
        x=int(idx.get("X", 0) or 0),
        y=int(idx.get("Y", 0) or 0),
        kind=(entry.get("Type") or {}).get("InventoryType", ""),
        damage=float(entry.get("DamageFactor", 0) or 0),
        special=(entry.get("Type") or {}).get("InventorySpecialSlotType", "")
                or tech.get("Gen", ""),
    )


def _read_inventory(inv: dict, key: str) -> Inventory:
    out = Inventory(key=key, label=INVENTORY_LABELS.get(key, key),
                    width=int(inv.get("Width", 0) or 0),
                    height=int(inv.get("Height", 0) or 0),
                    # Los huecos reales son ValidSlotIndices: Width*Height es
                    # solo la caja que rodea a la cuadrícula (120 celdas en el
                    # exotraje para 46 huecos reales).
                    capacity=len(inv.get("ValidSlotIndices") or []))
    for entry in inv.get("Slots") or []:
        if not isinstance(entry, dict) or not entry.get("Id"):
            continue
        slot = _slot_from_entry(entry)
        if slot:
            out.slots.append(slot)
    return out


def _hidden(inv: Inventory) -> bool:
    """Oculta las secciones 'Carga (legado)' si la partida no guarda nada ahí.

    El juego actual solo usa dos pestañas por contenedor; esa tercera quedó
    de versiones antiguas y en las partidas modernas viene siempre vacía.
    """
    return inv.key.endswith("_Cargo") and not inv.slots


def _player_state(root: dict) -> dict:
    """PlayerStateData del contexto activo (Main o Expedition)."""
    ctx = root.get("ActiveContext") or root.get("XTP") or "Main"
    contexts = root.get("Contexts") or {}
    base = contexts.get("Main") or root.get("BaseContext") or {}
    exp = contexts.get("Expedition") or root.get("ExpeditionContext") or {}
    chosen = exp if str(ctx).lower().startswith("expedition") and exp else base
    state = chosen.get("PlayerStateData") or root.get("PlayerStateData")
    if state is None:
        raise SaveError("no se encontró PlayerStateData en la partida")
    return state


def parse_save(path: Path, keymap: dict[str, str]) -> SaveData:
    raw = path.read_bytes()
    stat = path.stat()
    try:
        text = decompress_save(raw).rstrip(b"\x00").decode("utf-8", "replace")
        root = deobfuscate(json.loads(text), keymap)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise SaveError(f"JSON inválido en {path.name}: {exc}") from exc

    ps = _player_state(root)
    data = SaveData(path=path, mtime=stat.st_mtime, size=stat.st_size,
                    raw=root)
    common = root.get("CommonStateData") or {}
    data.save_name = str(common.get("SaveName") or "")
    data.summary = str(ps.get("SaveSummary") or "")
    data.game_mode = GAME_MODES.get(chosen_mode(root), "")
    data.timestamp = int(ps.get("TimeStamp", 0) or 0)
    data.units = int(ps.get("Units", 0) or 0)
    data.nanites = int(ps.get("Nanites", 0) or 0)
    data.quicksilver = int(ps.get("Specials", 0) or 0)
    data.vitals = {
        "health": _pct(ps.get("Health"), 100),
        "shield": _pct(ps.get("Shield"), 100),
        "energy": _pct(ps.get("Energy"), 100),
        # el juego no guarda el máximo de la nave: se muestran valores absolutos
        "ship_health": _pct(ps.get("ShipHealth"), 0),
        "ship_shield": _pct(ps.get("ShipShield"), 0),
        "ammo": {
            "Láser": int(ps.get("LaserAmmo", 0) or 0),
            "Escopeta": int(ps.get("ScatterAmmo", 0) or 0),
            "Pulso": int(ps.get("PulseAmmo", 0) or 0),
            "Rayo": int(ps.get("BoltAmmo", 0) or 0),
        },
    }

    # Exotraje
    for key, label in INVENTORY_LABELS.items():
        inv = ps.get(key)
        if isinstance(inv, dict) and isinstance(inv.get("Slots"), list):
            parsed = _read_inventory(inv, key)
            parsed.label = label
            parsed.group = "suit"
            parsed.active = True
            if not _hidden(parsed):
                data.inventories.append(parsed)

    # Naves: se leen TODAS las de la flota (no solo la activa) para poder ver
    # la carga de cualquier nave desde la interfaz.
    ships = [s for s in (ps.get("ShipOwnership") or [])
             if isinstance(s, dict)]
    active_ship = int(ps.get("PrimaryShip", 0) or 0)
    if not (0 <= active_ship < len(ships)):
        active_ship = 0
    data.ships = []
    for index, ship in enumerate(ships):
        base = str(ship.get("Name") or "").strip() or f"Nave {index + 1}"
        is_active = index == active_ship
        cargo = tech = cargo_cap = tech_cap = 0
        for key, suffix in (("Inventory", "Inventario"),
                            ("Inventory_Cargo", "Carga (legado)"),
                            ("Inventory_TechOnly", "Tecnología")):
            inv = ship.get(key)
            if not (isinstance(inv, dict) and isinstance(inv.get("Slots"), list)):
                continue
            parsed = _read_inventory(inv, f"ship{index}:{key}")
            parsed.label = f"{base} · {suffix}"
            parsed.group = "ship"
            parsed.active = is_active
            if _hidden(parsed) or (not parsed.slots and not is_active):
                continue
            data.inventories.append(parsed)
            if key == "Inventory":
                cargo, cargo_cap = len(parsed.slots), parsed.capacity
            elif key == "Inventory_TechOnly":
                tech, tech_cap = len(parsed.slots), parsed.capacity
        if not (cargo or tech):
            continue  # hueco libre de la flota
        data.ships.append({
            "key": f"ship{index}",
            "name": str(ship.get("Name") or ""),
            "label": base,
            "class": ((ship.get("Inventory") or {}).get("Class") or {})
                     .get("InventoryClass", ""),
            "active": is_active,
            "slots": cargo,
            "capacity": cargo_cap,
            "tech": tech,
            "tech_capacity": tech_cap,
        })

    # Multiherramientas: se leen todas las guardadas (Store), no solo la
    # equipada. "ActiveMultioolIndex" viene así de rubricado en el juego.
    tools = [tool for tool in (ps.get("Multitools") or [])
             if isinstance(tool, dict)]
    active_tool = int(ps.get("ActiveMultioolIndex", 0) or 0)
    data.multi_tools = []
    for index, tool in enumerate(tools):
        store = tool.get("Store")
        if not isinstance(store, dict) or not store.get("Slots"):
            continue
        parsed = _read_inventory(store, f"tool{index}:Store")
        if not parsed.slots:
            continue
        name = str(tool.get("Name") or "").strip()
        parsed.label = name or f"Multiherramienta {index + 1}"
        parsed.group = "multitool"
        parsed.active = index == active_tool
        data.inventories.append(parsed)
        data.multi_tools.append({
            "key": f"tool{index}",
            "name": name,
            "label": parsed.label,
            "class": (store.get("Class") or {}).get("InventoryClass", ""),
            "active": index == active_tool,
            "slots": len(parsed.slots),
            "capacity": parsed.capacity,
        })
    if not data.multi_tools:
        # Partidas antiguas: solo está la multiherramienta equipada.
        weapon = ps.get("WeaponInventory")
        if isinstance(weapon, dict) and isinstance(weapon.get("Slots"), list):
            parsed = _read_inventory(weapon, "WeaponInventory")
            parsed.label = "Multiherramienta"
            parsed.group = "multitool"
            parsed.active = True
            if parsed.slots:
                data.inventories.append(parsed)
                data.multi_tools.append({
                    "key": "WeaponInventory", "name": "", "label": parsed.label,
                    "class": (weapon.get("Class") or {}).get("InventoryClass", ""),
                    "active": True, "slots": len(parsed.slots),
                    "capacity": parsed.capacity,
                })

    # Carguero (freighter)
    for key, label in _FREIGHTER_LABELS.items():
        inv = ps.get(key)
        if isinstance(inv, dict) and isinstance(inv.get("Slots"), list):
            parsed = _read_inventory(inv, key)
            parsed.label = label
            parsed.group = "freighter"
            if not _hidden(parsed):
                data.inventories.append(parsed)

    # Contenedores del refugio y cajas varias
    for key, label in _EXTRA_INVENTORIES.items():
        inv = ps.get(key)
        if isinstance(inv, dict) and isinstance(inv.get("Slots"), list):
            parsed = _read_inventory(inv, key)
            parsed.label = label
            parsed.group = "storage"
            if parsed.slots:
                data.inventories.append(parsed)

    # Ubicación: la dirección galáctica del sistema actual (el mismo dato que
    # enseña el refuerzo de señal en formato XXXX:YYYY:ZZZZ:SSSS).
    universe = ps.get("UniverseAddress") or {}
    galactic = universe.get("GalacticAddress") or {}
    data.galaxy = int(universe.get("RealityIndex", 0) or 0)
    data.address = {
        "x": int(galactic.get("VoxelX", 0) or 0),
        "y": int(galactic.get("VoxelY", 0) or 0),
        "z": int(galactic.get("VoxelZ", 0) or 0),
        "system": int(galactic.get("SolarSystemIndex", 0) or 0),
        "planet": int(galactic.get("PlanetIndex", 0) or 0),
    }
    return data


def _pct(value, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def chosen_mode(root: dict) -> int:
    ctx = str(root.get("ActiveContext") or "Main")
    contexts = root.get("Contexts") or {}
    base = contexts.get("Main") or root.get("BaseContext") or {}
    exp = contexts.get("Expedition") or root.get("ExpeditionContext") or {}
    chosen = exp if ctx.lower().startswith("expedition") and exp else base
    return int(chosen.get("GameMode", 0) or 0)


def find_saves(root: Path | None = None) -> list[Path]:
    """Localiza los saves de todas las partidas instaladas."""
    base = root or Path.home() / "AppData/Roaming/HelloGames/NMS"
    if not base.exists():
        return []
    saves: list[Path] = []
    for profile in sorted(base.glob("st_*")):
        for pattern in ("save.hg", "save2.hg", "save3.hg", "save4.hg"):
            candidate = profile / pattern
            if candidate.exists():
                saves.append(candidate)
    return saves
