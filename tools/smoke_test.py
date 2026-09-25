"""Prueba rápida de los endpoints del servidor (python tools/smoke_test.py)."""
import json
import sys
import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:8765"


def get(path: str, **params):
    url = BASE + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=20) as res:
        return json.loads(res.read().decode("utf-8"))


def get_bytes(path: str):
    with urllib.request.urlopen(BASE + path, timeout=20) as res:
        return res.status, res.read()


def main() -> int:
    failures = []

    def check(label, condition, extra=""):
        print(("  OK   " if condition else "  FALLO") + f" {label} {extra}")
        if not condition:
            failures.append(label)

    status = get("/api/status")
    check("status: saves", len(status["saves"]) >= 1, f"({len(status['saves'])})")
    check("status: db", status["db"]["stats"]["items"] > 1000)

    inv = get("/api/inventory")
    check("inventory: inventarios", len(inv["inventories"]) >= 5,
          f"({len(inv['inventories'])})")
    check("inventory: totales", len(inv["totals"]) > 50)
    check("inventory: monedas", inv["wallet"]["units"] > 0)
    check("inventory: vitales", inv["vitals"]["health"] >= 0)

    for query in ("carbono", "carbon", "circuito", "ferrita"):
        results = get("/api/search", q=query)["results"]
        check(f"search '{query}'", len(results) > 0, f"({len(results)})")

    results = get("/api/search", q="carbono")["results"]
    item_id = results[0]["id"] if results else "FUEL1"
    detail = get("/api/item/" + urllib.parse.quote(item_id))
    check(f"item {item_id}", bool(detail["names"]), json.dumps(detail["names"], ensure_ascii=False))

    detail = get("/api/item/CASING")
    check("item CASING: receta", detail["craft"] is not None)
    check("item CASING: ingredientes", len(detail["craft"]["in"]) >= 1)

    refiners = [r for r in get("/api/search", q="nan")["results"]]
    check("búsqueda variada", len(refiners) > 0)

    # --- ronda 2: pares de save, clase de módulos, ids ilegibles, wiki ---
    pairs = {s["file"]: (s.get("pair"), s.get("newest")) for s in status["saves"]}
    check("status: saves agrupados por partida",
          all(p is not None for p, _ in pairs.values())
          and len({p for p, _ in pairs.values()}) >= 1, str(pairs))
    check("status: más reciente marcado",
          sum(1 for _, newest in pairs.values() if newest) <= 1
          and any(newest for _, newest in pairs.values()))

    slots = [s for inventory in inv["inventories"] for s in inventory["slots"]]
    check("inventory: ids ilegibles marcados",
          all("unknown" in s for s in slots),
          f"({sum(1 for s in slots if s.get('unknown'))} ilegibles)")

    classes = [item for item in inv["catalog"].values() if item.get("class")]
    check("inventory: clases de módulos", len(classes) > 5, f"({len(classes)})")
    check("db: módulos con clase",
          status["db"]["stats"].get("with_class", 0) > 100,
          f"({status['db']['stats'].get('with_class', 0)})")

    labels = [inventory["label"] for inventory in inv["inventories"]]
    check("inventory: 'Carguero'",
          any(label.startswith("Carguero") for label in labels)
          and not any("Nave de carga" in label for label in labels))
    check("inventory: taller de corbetas fuera",
          not any("corbeta" in label.lower() for label in labels))

    # Los iconos locales son opcionales a propósito: el ejecutable se
    # publica sin ellos (219 MB) y los deja para cuando el jugador los pide.
    detail = get("/api/item/PROC_LOOT")
    icon = detail.get("icon") or ""
    check("item PROC_LOOT: con icono (local o remoto)",
          icon.startswith("/icons/") or icon.startswith("http"), icon[:70])
    if icon.startswith("/icons/"):
        try:
            with urllib.request.urlopen(BASE + icon, timeout=20) as res:
                body = res.read()
            check("icono local servido por el servidor",
                  res.headers.get("Content-Type", "").startswith("image/")
                  and len(body) > 100, f"({len(body)} bytes)")
        except urllib.error.HTTPError as exc:
            # En una instalación recién hecha el catálogo aún no se ha
            # descargado: el servidor responde 404 y la casilla se queda con
            # las siglas, que es justo lo que tiene que pasar.
            check("icono local servido por el servidor (recién instalado: 404)",
                  exc.code == 404, f"HTTP {exc.code}")
        except Exception as exc:  # noqa: BLE001
            check("icono local servido por el servidor", False, str(exc))

    detail = get("/api/item/UP_JET2")
    check("item UP_JET2: clase", detail.get("class") in ("C", "B", "A", "S", "X", "?"),
          str(detail.get("class")))

    # un objeto catalogado sin nombre (clave de localización sin resolver)
    # debe seguir siendo consultable por su icono
    detail = get("/api/item/CV_INV1")
    check("item CV_INV1: sin nombre pero consultable",
          detail.get("icon") and not detail.get("names"))

    try:
        get("/api/item/NOEXISTE_ZZZ")
        check("item inexistente -> 404", False)
    except urllib.error.HTTPError as exc:
        check("item inexistente -> 404", exc.code == 404)

    # --- fase 1: flota, dirección, filtros y plan de crafteo ---
    groups = {inventory.get("group") for inventory in inv["inventories"]}
    check("inventory: secciones agrupadas",
          {"suit", "ship"} <= groups, str(sorted(g for g in groups if g)))
    check("inventory: flota completa (naves y multiherramientas)",
          {"ship", "multitool"} <= groups
          and len(inv["inventories"]) >= 12,
          f"({len(inv['inventories'])} secciones)")
    keys = [inventory["key"] for inventory in inv["inventories"]]
    check("inventory: claves de sección únicas", len(keys) == len(set(keys)))
    check("inventory: capacidad real por contenedor",
          all(inventory.get("capacity", 0) >= len(inventory["slots"])
              for inventory in inv["inventories"]))
    check("inventory: contenedores marcados como activos",
          sum(1 for i in inv["inventories"] if i.get("active")) >= 2,
          f"({sum(1 for i in inv['inventories'] if i.get('active'))})")
    check("inventory: naves con clase y estado",
          len(inv.get("ships", [])) >= 1
          and all(ship.get("class") and "active" in ship for ship in inv["ships"]),
          str([(s["label"], s["class"], s["active"]) for s in inv.get("ships", [])]))
    check("inventory: multiherramientas expuestas",
          len(inv.get("multitools", [])) >= 1,
          str([t["label"] for t in inv.get("multitools", [])]))

    address = inv["save"].get("address") or {}
    parts = address.get("hex", "").split(":")
    check("save: dirección en formato comunidad XXXX:YYYY:ZZZZ:SSSS",
          len(parts) == 4 and all(len(p) == 4
                                  and all(c in "0123456789ABCDEF" for c in p)
                                  for p in parts),
          str(address.get("hex")))
    voxel = address.get("voxel") or {}
    check("save: la dirección sale de VoxelX/Y/Z (+2047 / +127)",
          len(parts) == 4 and {"x", "y", "z"} <= set(voxel)
          and (int(parts[0], 16) - voxel["x"]) % 4096 == 2047
          and (int(parts[1], 16) - voxel["y"]) % 256 == 127
          and (int(parts[2], 16) - voxel["z"]) % 4096 == 2047
          and int(parts[3], 16) == address.get("system", 0) % 65536,
          f"voxel={voxel}")
    check("save: galaxia y tiempo de juego",
          isinstance(inv["save"].get("galaxy"), int)
          and inv["save"].get("play_time", 0) > 0,
          f"galaxia={inv['save'].get('galaxy')} "
          f"tiempo={inv['save'].get('play_time')}s")

    craft = get("/api/craftable", kind="craft")["results"]
    check("craftable: fabricables ahora", len(craft) > 5, f"({len(craft)})")
    check("craftable: veces y receta completas",
          all(item.get("times", 0) >= 1 and item.get("need")
              for item in craft))
    refine = get("/api/craftable", kind="refine")["results"]
    check("craftable: refinables ahora", len(refine) > 5, f"({len(refine)})")
    check("craftable: tipo desconocido cae a fabricación",
          get("/api/craftable", kind="zzz")["kind"] == "craft")

    if craft:
        plan = get("/api/plan/" + urllib.parse.quote(craft[0]["id"]), n=1)
        check("plan: fabricable ahora sin faltantes",
              plan["shopping"] == [],
              str([(s["id"], s["need"]) for s in plan["shopping"]]))

    plan = get("/api/plan/NOEXISTE_ZZZ", n=3)
    check("plan: id sin receta queda como falta",
          plan["root"]["id"] == "NOEXISTE_ZZZ"
          and plan["root"]["missing"] >= 3
          and len(plan["shopping"]) == 1,
          str([(s["id"], s["need"]) for s in plan["shopping"]]))
    check("plan: cantidad mínima respetada",
          get("/api/plan/CASING", n="0")["root"]["need"] >= 1)

    update = get("/api/update/state")
    check("update: estado del actualizador",
          {"running", "count", "lines", "exit"} <= set(update)
          and isinstance(update["running"], bool)
          and isinstance(update["lines"], list),
          f"running={update['running']} líneas={update['count']}")

    status, blob = get_bytes("/glyphs/0.png")
    check("estáticos: glifos de portal servidos",
          status == 200 and blob.startswith(b"\x89PNG") and len(blob) > 1000,
          f"{status}, {len(blob)} B")

    catalog = list((inv.get("catalog") or {}).values())
    locales = [c for c in catalog if (c.get("icon") or "").startswith("/icons/")]
    remotos = [c for c in catalog if (c.get("icon") or "").startswith("http")]
    if len(locales) > len(catalog) * 0.5:
        # Con el catálogo descargado: los iconos tienen que servirse de local.
        check("iconos: el catálogo se sirve desde data/icons",
              len(locales) >= len(catalog) * 0.9,
              f"{len(locales)}/{len(catalog)} locales")
        status, blob = get_bytes(locales[0]["icon"])
        check("iconos: fichero local servido como imagen",
              status == 200 and len(blob) > 200,
              f"{locales[0]['icon']} -> {status}, {len(blob)} B")
    else:
        # Instalación recién hecha: aún no se han bajado los iconos y todo
        # apunta a las URL comunitarias, que es el estado por defecto.
        print(f"  --    iconos: todavía sin descargar "
              f"({len(remotos)} remotos; se Bajan con «Actualizar datos»)")

    print()
    if failures:
        print("FALLAN:", ", ".join(failures))
        return 1
    print("Todo correcto.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
