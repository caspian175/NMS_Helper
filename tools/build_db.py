"""Construye data/db.json a partir de las fuentes descargadas por update_db.py.

Fuentes:
  * nmstoolkit items.json      -> IDs de juego (los mismos que usa el save)
  * NMS-Handbook JSON_Files    -> recetas de crafteo y refinado + textos EN
  * AssistantNMS (npm)         -> nombres/descripciones ES + iconos CDN
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

from _common import DATA, DL, ROOT  # noqa: E402  (rutas también al empaquetar)


def norm(text: str) -> str:
    text = (text or "").lower()
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


# Marcas de formato del texto del juego: <FUEL>carbono<>, <NEWLINE>, <b>...
TAG_RE = re.compile(r"</?[A-Z_0-9]*>")
# Icono embebido: <IMG>FE_ALT1<>, <IMG>PR_10<> (sin texto legible).
IMG_RE = re.compile(r"<IMG>[^<>]*<>", re.IGNORECASE)
# Clave de interfaz que otra fuente ya dejó sin marcas: "…with FE_ALT1."
UI_KEY_RE = re.compile(r"\bFE_[A-Z0-9_]+\b")


def clean_text(text: str, placeholder: str = "") -> str:
    """Quita las marcas del juego y normaliza los espacios resultantes.

    'placeholder' sustituye a los iconos de interfaz (para no dejar la
    frase con un hueco); si es vacío, simplemente se eliminan."""
    text = re.sub(r"<NEWLINE>", "\n", text, flags=re.IGNORECASE)
    text = IMG_RE.sub(placeholder, text)
    text = UI_KEY_RE.sub(placeholder, text)
    text = TAG_RE.sub("", text)
    text = re.sub(r"[ \t]{2,}", " ", text)       # huecos dobles
    text = re.sub(r" +([,.;:?!])", r"\1", text)  # espacio antes de signo
    return text.strip()


def hex_color(r: float, g: float, b: float) -> str:
    try:
        return "{:02X}{:02X}{:02X}".format(
            max(0, min(255, int(round(float(r) * 255)))),
            max(0, min(255, int(round(float(g) * 255)))),
            max(0, min(255, int(round(float(b) * 255)))))
    except (TypeError, ValueError):
        return ""


# PNGs que el repositorio NMS-Handbook todavía no tiene (comprobado con
# peticiones reales): mejor dejar que se use el icono de Assistant si existe.
HANDBOOK_MISSING = {
    "missionfaction.gek", "missionfaction.korvax", "missionfaction.vykeen",
    "missionfaction.builder", "building.settlement", "emptyslotcircle",
}

# Tablas complementarias del Handbook, con el mismo esquema que Product_Table
# (ProductId / NameLower_Text / Icon_Filename). Solo rellenan huecos: no
# cambian el tipo ni pisan los textos de las cinco tablas principales.
EXTRA_TABLES = [
    "Building_Parts_Table.json", "Legacy_Item_Table.json",
    "Corvette_Parts_Table.json", "Ship_Part_Table.json",
    "Special_Purchase_Table.json", "Special_Rewards_Table.json",
    "Bait_Table.json", "Fossil_Table.json", "Fish_Table.json",
    "Purchaseable_Building_Blueprints.json",
]

# Nombres que en realidad son una clave de localización sin traducir
# ("UT_CR_MINE_NAME_L"): mejor no mostrarlas como si fueran el nombre.
LOC_KEY_RE = re.compile(r"^[A-Z]{2,}(?:_[A-Z0-9]+){2,}$")


def loc_key(text: str) -> bool:
    text = (text or "").strip()
    return len(text) > 4 and LOC_KEY_RE.match(text) is not None



def dds_to_png_url(icon: str) -> str:
    """TEXTURES/UI/FRONTEND/ICONS/U4SUBSTANCES/SUBSTANCE.FUEL.1.DDS
    -> URL raw del repositorio NMS-Handbook (que guarda los PNG en minúsculas)."""
    if not icon or not icon.upper().endswith(".DDS"):
        return ""
    sha = "142d9ffd8078944722243398202f22cbef47cd02"
    rel = icon[:-4] + ".png"
    parts = rel.split("/")
    rel = "/".join(parts[:4] + [p.lower() for p in parts[4:]])
    if parts[-1].rsplit(".", 1)[0].lower() in HANDBOOK_MISSING:
        return ""
    return f"https://raw.githubusercontent.com/ApexFatality93/NMS-Handbook/{sha}/{rel}"


def assistant_icon(entry: dict) -> str:
    """URL del icono en el CDN de AssistantNMS.

    Solo 'CdnUrl' es fiable: la ruta relativa 'Icon' no siempre existe en
    el CDN (≈85 % de 404 al sondear), así que no se deriva de ahí."""
    if not isinstance(entry, dict):
        return ""
    return entry.get("CdnUrl") or ""


def load_assistant(folder: str) -> dict[str, dict]:
    items: dict[str, dict] = {}
    base = DL / "lang" / folder
    if not base.exists():
        return items
    for path in sorted(base.glob("*.lang.json")):
        if path.name in ("Refinery.lang.json", "SeasonalExpedition.lang.json",
                         "AlienPuzzle.lang.json"):
            continue
        try:
            entries = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if isinstance(entry, dict) and entry.get("Id") and entry.get("Name"):
                items.setdefault(entry["Id"], entry)
    return items


def load_refining_assistant(folder: str) -> list[dict]:
    path = DL / "lang" / folder / "Refinery.lang.json"
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def _op_text(operation: str) -> str:
    """'Requested Operation: Extract Chromatic Material' -> 'Extract ...'"""
    operation = (operation or "").strip()
    if ":" in operation:
        return operation.split(":", 1)[1].strip()
    return operation


# ----------------------------------------------------------------------
# Clase de los módulos (C/B/A/S/X/?)
CLASS_PREFIX_RE = re.compile(r"^([CBAS])-Class\b", re.IGNORECASE)
# sufijo del ID -> clase cuando el nombre no la indica
CLASS_SUFFIX = {"1": "C", "2": "B", "3": "A", "4": "S", "X": "X", "0": "?"}
MODULE_PREFIXES = ("UP_", "U_", "CV_")


def module_class(item_id: str, name_en: str) -> str:
    """Clase/rango de un módulo de tecnología, si lo tiene.

    El nombre del juego es lo primero ("B-Class Life Support Upgrade" o
    "Illegal Mining Beam Upgrade"); si no lo trae, se usa el sufijo del ID,
    que sigue la escala C=1, B=2, A=3, S=4, X=ilegal, 0=oxidado(?)."""
    if not item_id.startswith(MODULE_PREFIXES + ("SHIP_CORE_",)):
        return ""
    match = CLASS_PREFIX_RE.match((name_en or "").strip())
    if match:
        return match.group(1).upper()
    lowered = (name_en or "").lower()
    if "illegal" in lowered or "suspicious" in lowered:
        return "X"
    if "rusted" in lowered:
        return "?"
    if "anomalous" in lowered:
        return "?"
    return CLASS_SUFFIX.get(item_id[-1], "")


# ----------------------------------------------------------------------
# Iconos de la wiki (fuente de último recurso)
WIKI_API = "https://nomanssky.fandom.com/api.php"
WIKI_HEADERS = {"User-Agent": "nms-helper/1.0 (iconos de la wiki)"}


def wiki_get(params: dict) -> dict:
    url = f"{WIKI_API}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers=WIKI_HEADERS)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def wiki_file_url(name: str) -> str:
    """URL directa de 'File:<name>' en el CDN de la wiki."""
    data = wiki_get({"action": "query", "titles": f"File:{name}",
                     "prop": "imageinfo", "iiprop": "url", "format": "json"})
    for page in data.get("query", {}).get("pages", {}).values():
        info = page.get("imageinfo")
        if info:
            return info[0].get("url", "")
    return ""


def wiki_page_image(title: str) -> str:
    """Imagen del infobox de la página 'title' (vacía si no tiene)."""
    data = wiki_get({"action": "parse", "page": title, "prop": "wikitext",
                     "format": "json", "redirects": "1"})
    if "error" in data:
        return ""
    wikitext = data.get("parse", {}).get("wikitext", {}).get("*", "")
    match = re.search(r"\|\s*image\s*=\s*([^\n|]+)", wikitext, re.IGNORECASE)
    if not match:
        return ""
    value = match.group(1).strip()
    inner = re.search(r"\[\[[Ff]ile:([^\]|]+)", value)
    name = (inner.group(1) if inner else value).strip()
    name = re.sub(r"^File:", "", name, flags=re.IGNORECASE).strip()
    if not name or name.lower() in ("none", "-", "noimage"):
        return ""
    return wiki_file_url(name)


def wiki_icon(name_en: str, cache: dict) -> str:
    """Icono de la wiki para el objeto con ese nombre (con caché)."""
    key = norm(name_en)
    if not key or key in cache:
        return cache.get(key, "")
    url = wiki_page_image(name_en)
    if not url:
        # el título exacto no existe: se busca y se usa el que coincida
        found = wiki_get({"action": "query", "list": "search",
                          "srsearch": name_en, "srlimit": "5",
                          "format": "json"})
        for hit in found.get("query", {}).get("search", []):
            if norm(hit.get("title", "")) == key:
                url = wiki_page_image(hit["title"])
                break
    cache[key] = url
    return url


# Iconos descargados: se guardan en data/icons/ y se sirven desde el propio
# servidor (/icons/...). El CDN de la wiki no siempre responde cuando otra
# página lo pide (bloqueadores, hotlink protection) y así también funcionan
# sin conexión.
ICONS_DIR = DATA / "icons"
ICON_EXT_RE = re.compile(r"\.(png|jpe?g|gif|webp|svg)$", re.IGNORECASE)


def localize_icon(url: str, item_id: str) -> str:
    """Descarga el icono a data/icons/ y devuelve su ruta local.

    Si la descarga falla se devuelve la URL original (la remota sigue
    siendo mejor que nada)."""
    if not url or url.startswith("/"):
        return url
    try:
        ICONS_DIR.mkdir(parents=True, exist_ok=True)
        suffix = Path(urllib.parse.urlsplit(url).path).suffix
        if not ICON_EXT_RE.search(suffix):
            suffix = ".png"
        name = re.sub(r"[^A-Za-z0-9_.-]", "_", item_id) + suffix.lower()
        request = urllib.request.Request(url, headers=WIKI_HEADERS)
        with urllib.request.urlopen(request, timeout=30) as response:
            data = response.read()
        if len(data) < 64:
            return url
        (ICONS_DIR / name).write_bytes(data)
        return f"/icons/{name}"
    except Exception:  # noqa: BLE001
        return url


def save_item_ids() -> set[str]:
    """IDs que aparecen en las partidas locales.

    Acota las consultas a la wiki a lo que realmente se va a ver (si no,
    serían cientos de peticiones por cada objeto sin icono)."""
    try:
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        from nms_helper import save as save_mod
        keymap = save_mod.load_keymap(DATA / "jsonmap.txt")
        ids: set[str] = set()
        for path in save_mod.find_saves():
            try:
                data = save_mod.parse_save(path, keymap)
            except Exception:  # noqa: BLE001
                continue
            for inventory in data.inventories:
                for slot in inventory.slots:
                    ids.add(slot.id.lstrip("^").split("#")[0])
        return ids
    except Exception:  # noqa: BLE001
        return set()


def main() -> int:
    required = ["items_nmstoolkit.json", "Crafting_Table.json",
                "Refining_Table.json", "Substance_Table.json",
                "Product_Table.json", "Technology_Table.json"]
    missing = [name for name in required if not (DL / name).exists()]
    if missing or not (DL / "lang" / "en").exists():
        print("Faltan datos descargados. Ejecuta primero: python tools/update_db.py")
        if missing:
            print("  faltan:", ", ".join(missing))
        return 1

    nmstoolkit = json.loads((DL / "items_nmstoolkit.json").read_text(encoding="utf-8"))
    crafting = json.loads((DL / "Crafting_Table.json").read_text(encoding="utf-8"))
    refining = json.loads((DL / "Refining_Table.json").read_text(encoding="utf-8"))
    substance = json.loads((DL / "Substance_Table.json").read_text(encoding="utf-8"))
    products = json.loads((DL / "Product_Table.json").read_text(encoding="utf-8"))
    technology = json.loads((DL / "Technology_Table.json").read_text(encoding="utf-8"))

    assistant_en = load_assistant("en")
    assistant_es = load_assistant("es")
    refining_es = load_refining_assistant("es")

    # índice: nombre en inglés (normalizado) -> entrada de AssistantNMS
    assistant_by_name: dict[str, dict] = {}
    for entry in assistant_en.values():
        assistant_by_name.setdefault(norm(entry.get("Name", "")), entry)

    items: dict[str, dict] = {}

    def put(item_id: str, **fields) -> dict:
        item_id = item_id.lstrip("^")
        entry = items.setdefault(item_id, {"id": item_id})
        for key, value in fields.items():
            if value in (None, "", [], {}) and key in entry:
                continue
            entry[key] = value
        return entry

    # 1) IDs de juego con sus textos base (nmstoolkit)
    for raw in nmstoolkit:
        item_id = str(raw.get("id", "")).lstrip("^")
        if not item_id or raw.get("name") in (None, ""):
            continue
        entry = put(item_id)
        if not loc_key(raw.get("name", "")):
            entry.setdefault("name", {})["en"] = raw.get("name", "")
        entry["type"] = raw.get("type", "") or entry.get("type", "")
        if raw.get("symbol"):
            entry["symbol"] = raw["symbol"]
        if raw.get("subtitle"):
            entry["group"] = raw["subtitle"]
        if raw.get("category"):
            entry["category"] = raw["category"]
        if raw.get("description"):
            entry.setdefault("desc", {})["en"] = raw["description"]

    # 2) Tablas del Handbook: refuerzan nombres, colores, iconos y categorías
    handbook_tables = {
        "substance": substance,
        "product": products,
        "technology": technology,
    }
    for kind, table in handbook_tables.items():
        for key, row in table.items():
            item_id = key.lstrip("^")
            entry = put(item_id)
            entry["type"] = kind
            name = row.get("NameLower_Text") or row.get("Name_Text") or ""
            if name and not loc_key(name):
                entry.setdefault("name", {})["en"] = name
            desc = row.get("Description_Text")
            if desc:
                entry.setdefault("desc", {})["en"] = desc
            color = hex_color(row.get("Colour_R"), row.get("Colour_G"),
                              row.get("Colour_B"))
            if color:
                entry["color"] = color
            icon = dds_to_png_url(row.get("Icon_Filename", ""))
            if icon:
                entry["icon"] = icon
            if row.get("BaseValue"):
                try:
                    entry["value"] = int(float(row["BaseValue"]))
                except ValueError:
                    pass
            group = row.get("Subtitle_Text")
            if group:
                entry["group"] = group
            if row.get("Type"):
                entry.setdefault("kind", row["Type"])

    # 2b) Tablas complementarias del Handbook: solo rellenan huecos (icono y
    #     nombre de piezas de edificio, objetos legados, módulos de corbeta…),
    #     sin tocar el tipo ni los textos que ya están resueltos.
    extra_rows = 0
    for table_name in EXTRA_TABLES:
        path = DL / table_name
        if not path.exists():
            continue
        try:
            extra_table = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        for key, row in extra_table.items():
            if not isinstance(row, dict):
                continue
            name = row.get("NameLower_Text") or row.get("Name_Text") or ""
            if not name or loc_key(name):
                continue
            entry = put(key)
            extra_rows += 1
            entry.setdefault("name", {}).setdefault("en", name)
            desc = row.get("Description_Text")
            if desc:
                entry.setdefault("desc", {}).setdefault("en", desc)
            if not entry.get("icon"):
                icon = dds_to_png_url(row.get("Icon_Filename", ""))
                if icon:
                    entry["icon"] = icon
            if not entry.get("color"):
                color = hex_color(row.get("Colour_R"), row.get("Colour_G"),
                                  row.get("Colour_B"))
                if color:
                    entry["color"] = color
            if not entry.get("group") and row.get("Subtitle_Text"):
                entry["group"] = row["Subtitle_Text"]
            if entry.get("value") is None and row.get("BaseValue"):
                try:
                    entry["value"] = int(float(row["BaseValue"]))
                except ValueError:
                    pass

    # 3) Cruzar con AssistantNMS -> nombres y descripciones en español.
    #    El icono solo se toma de Assistant si no existe ya el del Handbook:
    #    el Handbook extrae los DDS del juego (fuente autoritativa) mientras
    #    que el CDN de Assistant sirve algún fichero obsoleto para ítems como
    #    OXYGEN o módulos procedurales (auditoría: 80 de 734 no cuadraban).
    matched = 0
    for entry in items.values():
        name_en = (entry.get("name") or {}).get("en", "")
        key = norm(name_en)
        if not key:
            continue
        assistant = assistant_by_name.get(key)
        if not assistant:
            continue
        matched += 1
        entry["assistant_id"] = assistant["Id"]
        entry["icon"] = entry.get("icon") or assistant_icon(assistant) or ""
        if assistant.get("Colour"):
            entry["color"] = assistant["Colour"]
        if assistant.get("MaxStackSize"):
            entry["stack"] = int(assistant["MaxStackSize"])
        if assistant.get("BaseValueUnits") is not None:
            entry["value"] = int(assistant["BaseValueUnits"])
        if assistant.get("Group"):
            entry["group"] = assistant["Group"]
        localized = assistant_es.get(assistant["Id"])
        if localized:
            entry.setdefault("name", {})["es"] = localized.get("Name", "")
            if localized.get("Description"):
                entry.setdefault("desc", {})["es"] = localized["Description"]
        if assistant.get("Description"):
            entry.setdefault("desc", {})["en"] = assistant["Description"]

    # 4) Recetas de crafteo (tabla del juego)
    recipes: dict[str, dict] = {}
    for product_id, row in crafting.items():
        ingredients = row.get("Ingredients") or []
        if not ingredients:
            continue
        recipes[product_id.lstrip("^")] = {
            "out": 1,
            "in": [
                {"id": str(ing.get("Id", "")).lstrip("^"),
                 "amount": int(ing.get("Amount", 1) or 1)}
                for ing in ingredients if ing.get("Id")
            ],
        }

    # 5) Recetas de refinado
    refine_list: list[dict] = []
    for out_id, row in refining.items():
        for recipe in row.get("Recipes") or []:
            inputs = [
                {"id": str(ing.get("Id", "")).lstrip("^"),
                 "amount": int(ing.get("Amount", 1) or 1)}
                for ing in (recipe.get("Ingredients") or []) if ing.get("Id")
            ]
            if not inputs:
                continue
            refine_list.append({
                "out": {"id": out_id.lstrip("^"),
                        "amount": int(recipe.get("Amount", 1) or 1)},
                "in": inputs,
                "time": float(recipe.get("TimeToMake", 0) or 0),
                "op": recipe.get("RecipeName", ""),
            })

    # Nombre de la operación en español: Assistant publica la tabla de
    # refinería en EN y ES con los mismos Id (ref1..), así que se emparejan
    # por Id y se les quita el prefijo "Requested Operation: ".
    op_es: dict[str, str] = {}
    refining_en = load_refining_assistant("en")
    if refining_en and refining_es:
        es_by_id = {e.get("Id"): e.get("Operation", "") for e in refining_es
                    if isinstance(e, dict)}
        for entry in refining_en:
            if not isinstance(entry, dict):
                continue
            en = _op_text(entry.get("Operation", ""))
            es = _op_text(es_by_id.get(entry.get("Id"), ""))
            if en and es:
                op_es.setdefault(en, es)
    for recipe in refine_list:
        recipe["op_es"] = op_es.get(recipe["op"], "")

    # 6) Módulos de tecnología procedural (UP_*): la base comunitaria no
    #    publica su traducción ni su icono, pero sí los de la tecnología
    #    base a la que mejoran ("C-Class Mining Beam Upgrade" -> "Mining
    #    Beam"). Buscamos la subcadena más larga del nombre que exista,
    #    primero en AssistantNMS (CDN) y después en el Handbook (GitHub).
    #    Casos sin nombre equivalente en la base comunitaria:
    extra_bases = {
        "salvaged upgrade components": "salvaged data",
    }
    handbook_by_name: dict[str, dict] = {}
    handbook_by_id: dict[str, dict] = {}
    for table in handbook_tables.values():
        for key, row in table.items():
            handbook_by_id[key.lstrip("^")] = row
            name = row.get("NameLower_Text") or row.get("Name_Text") or ""
            if name:
                handbook_by_name.setdefault(norm(name), row)

    # Módulos cuyo nombre genérico no coincide con ninguna entrada de las
    # bases comunitarias: se apunta a la fila equivalente del Handbook.
    handbook_fallback = {
        "UP_SENGUN": "U_SENTGUN",      # Forbidden Multi-Tool Module
        "UP_SNSUIT": "U_SENTSUIT",     # Forbidden Exosuit Module
        "UP_RBSUIT": "BP_SALVAGE",     # Salvaged Upgrade Components
        "UP_MFIRE2": "U_MECHFLAME2",   # Minotaur Flamethrower Upgrade
        "UP_MFIRE3": "U_MECHFLAME2",
        "UP_MFIRE4": "U_MECHFLAME2",
    }
    # Módulos de flota: todos se llaman "Salvaged Freighter Module" pero
    # cada familia tiene su unidad equivalente en el Handbook (el sufijo
    # numérico de calidad se quita al buscar).
    handbook_fallback.update({
        "UP_FRHYP": "U_FR_HYP1",
        "UP_FRSPE": "U_FR_SPE1",
        "UP_FRFUE": "U_FR_FUEL1",
        "UP_FRCOM": "U_FR_COM1",
        "UP_FRTRA": "U_FR_TRA1",
        "UP_FREXP": "U_FR_EXP1",
        "UP_FRMIN": "U_FR_MINE1",
    })
    # Módulos de corbeta (CV_*): ninguna fuente tiene todavía su nombre
    # (sigue sin resolverse la clave UT_CR_*_NAME_L), pero el Handbook sí
    # publica la fila equivalente con el icono de cada familia.
    handbook_fallback.update({
        "CV_FIT": "U_CRFIGHT1",   # corbeta de combate
        "CV_SCI": "U_CRSCI1",     # corbeta científica
        "CV_TRA": "U_CRTRADE1",   # corbeta comercial
        "CV_INV": "U_CRMINE1",    # corbeta minera
    })

    def base_hit(words: list[str]) -> dict | None:
        """Entrada del Handbook (DDS del juego) o AssistantNMS de la tecnología base."""
        for start in range(len(words)):
            for end in range(len(words), start, -1):
                key = " ".join(words[start:end])
                tech = handbook_by_name.get(key)
                if tech and dds_to_png_url(tech.get("Icon_Filename", "")):
                    return tech
                hit = assistant_by_name.get(key)
                if hit and hit.get("CdnUrl"):
                    return hit
        return None

    def hit_icon(hit: dict) -> str:
        if not hit:
            return ""
        return dds_to_png_url(hit.get("Icon_Filename", "")) \
            or hit.get("CdnUrl", "")

    recovered_icons = 0
    for item_id, entry in items.items():
        if entry.get("icon"):
            continue
        name_en = (entry.get("name") or {}).get("en", "")
        words = norm(name_en).split()
        # fallback fijo por ID (también sirve para los objetos cuyo nombre
        # sigue sin resolverse y por tanto no tienen `words`)
        forced_id = (handbook_fallback.get(item_id)
                     or handbook_fallback.get(item_id.rstrip("0123456789")))
        # solo módulos (UP_*) y objetos llamados "... Upgrade"/"... Module":
        # así evitamos asignar un icono cualquiera al resto de sin-icono.
        if not forced_id and (not words or not (
                item_id.startswith("UP_")
                or words[-1] in ("upgrade", "module"))):
            continue
        # cada paso solo se acepta si aporta una URL de verdad
        hit = None
        icon = ""
        forced = extra_bases.get(" ".join(words))
        if forced:
            hit = assistant_by_name.get(forced)
            icon = hit_icon(hit)
        if not icon:
            hit = base_hit(words)
            icon = hit_icon(hit)
        # fallbacks por ID para los nombres genéricos
        if not icon and forced_id:
            hit = handbook_by_id.get(forced_id, None)
            icon = hit_icon(hit)
        if icon:
            entry["icon"] = icon
            recovered_icons += 1
            if hit.get("Colour"):
                entry["color"] = hit["Colour"]

    # 6b) Clase de los módulos de tecnología (C/B/A/S/X/?).
    #     El juego la codifica en el propio nombre ("B-Class … Upgrade",
    #     "Illegal/Suspicious …", "Rusted …") y, cuando el nombre no la trae,
    #     en el sufijo del ID: 1=C, 2=B, 3=A, 4=S, X=ilegal, 0=oxidado(?).
    with_class = 0
    for item_id, entry in items.items():
        cls = module_class(item_id, (entry.get("name") or {}).get("en", ""))
        if cls:
            entry["class"] = cls
            with_class += 1

    # 6c) Último recurso para los iconos: la wiki de No Man's Sky.
    #     Solo se consulta por los objetos que aparecen en tus partidas y que
    #     las otras fuentes no cubren (p. ej. "Unearthed Treasure"), y los
    #     resultados quedan cacheados en tools/_dl/wiki_icons.json.
    wiki_cache_path = DL / "wiki_icons.json"
    wiki_cache: dict[str, str] = {}
    if wiki_cache_path.exists():
        try:
            wiki_cache = json.loads(wiki_cache_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            wiki_cache = {}
    wiki_added = 0
    cache_before = dict(wiki_cache)
    pending = []
    for item_id in sorted(save_item_ids()):
        entry = items.get(item_id)
        if not entry or entry.get("icon"):
            continue
        name_en = (entry.get("name") or {}).get("en", "")
        if not name_en:
            continue
        pending.append((item_id, name_en))
    for item_id, name_en in pending:
        try:
            icon = wiki_icon(name_en, wiki_cache)
        except Exception as exc:  # noqa: BLE001
            print(f"  ! wiki no disponible ({exc}); se omite este paso")
            break
        if icon:
            items[item_id]["icon"] = localize_icon(icon, item_id)
            wiki_added += 1
    if wiki_cache != cache_before:
        wiki_cache_path.write_text(json.dumps(wiki_cache, ensure_ascii=False,
                                              indent=0), encoding="utf-8")

    # 7) Los textos del juego traen marcas que no son texto plano:
    #      <FUEL>carbono<>  -> coloreado: se queda "carbono"
    #      <IMG>FE_ALT1<>   -> icono de interfaz sin nombre legible
    #      <NEWLINE>        -> salto de línea
    #    En los nombres el icono se descarta; en las descripciones se deja
    #    un marcador legible para no romper la frase.
    for entry in items.values():
        names = entry.get("name") or {}
        for lang, text in list(names.items()):
            if isinstance(text, str):
                names[lang] = clean_text(text)
        descs = entry.get("desc") or {}
        for lang, text in list(descs.items()):
            if isinstance(text, str):
                placeholder = "[icono]" if lang.startswith("es") else "[icon]"
                descs[lang] = clean_text(text, placeholder)

    DATA.mkdir(exist_ok=True)
    (DATA / "db.json").write_text(
        json.dumps({
            "built_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "sources": {
                "nmstoolkit": "https://github.com/pljeroen/nmstoolkit",
                "handbook": "https://github.com/ApexFatality93/NMS-Handbook",
                "assistant": "https://www.nmsassistant.com/",
            },
            "stats": {
                "items": len(items),
                "crafting_recipes": len(recipes),
                "refining_recipes": len(refine_list),
                "spanish_names": matched,
                "with_class": with_class,
                "wiki_icons": wiki_added,
            },
            "items": items,
            "crafting": recipes,
            "refining": refine_list,
        }, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8")

    print(f"Objetos: {len(items)} ({matched} con nombre en español)")
    print(f"Recetas de crafteo: {len(recipes)}")
    print(f"Recetas de refinado: {len(refine_list)}")
    if pending:
        print(f"Iconos tomados de la wiki: {wiki_added} de {len(pending)}"
              f" consultados")
    print(f"Módulos con clase: {with_class}")
    print(f"Escrito: {DATA / 'db.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
