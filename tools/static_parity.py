"""Compara la API estática de la web (web/static-db.js) con nms_helper/db.py.

La web publicada (GitHub Pages) contesta /api/* en el navegador; aquí se
calcula lo mismo con el código de Python para unas consultas de muestra y se
enfrentan los resultados con node. Actions lo ejecuta antes de publicar
(--require-node) para que la implementación JavaScript no se descuelgue de la
de Python.

    python tools/static_parity.py                 # si hay node instalado
    python tools/static_parity.py --require-node  # sin node, falla (CI)
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from nms_helper.db import GameDB  # noqa: E402

# Búsquedas: español, frase, raíz corta, sin resultados, con ñ/tilde,
# una sola letra y solo espacios (que debe devolver vacío).
BUSQUEDAS = [
    "carbono",
    "circuito de vuelo",
    "refin",
    "zzz-no-existe",
    "ñandú",
    "a",
    "  ",
]

PLANES = [
    ["CASING", 3],
    ["CASING", 0],       # la cantidad mínima la fija plan()
    ["TECHFRAG", 5],
    ["NOEXISTE_ZZZ", 3],
]

RUTAS = [
    "/api/status",
    "/api/search?q=carbono",
    "/api/item/CASING",
    "/api/item/NOEXISTE_ZZZ",
    "/api/craftable?kind=refine",
    "/api/plan/CASING?n=0",
    "/api/plan/CASING?n=abc",
]


def craftable_todas(db: GameDB, kind: str) -> list[dict]:
    """Referencia de «todas las recetas» para la web.

    El programa local lista solo lo ejecutable con lo que hay (db.craftable
    con totales); la web no lee partidas, así que enseña la receta entera y
    sin el contador `times`. Esto usa las primitivas de db.py (resumen,
    nombres y criterio de ordenación) para enfrentarlas a static-db.js.
    """
    if kind == "refine":
        entradas = [(r["out"]["id"], r, int(r["out"].get("amount", 1) or 1), True)
                    for r in db.refining]
    else:
        entradas = [(pid, r, int(r.get("out", 1) or 1), False)
                    for pid, r in db.crafting.items()]
    resultados = []
    for pid, receta, salida, es_refino in entradas:
        resumen = db._summary(pid)
        resumen.update({
            "out": salida,
            "need": [dict(ing, names=db._names(ing["id"]))
                     for ing in receta["in"]],
        })
        if es_refino:
            resumen.update({"time": receta.get("time", 0),
                            "op": receta.get("op", ""),
                            "op_es": receta.get("op_es", "")})
        resultados.append(resumen)
    resultados.sort(key=lambda it: (db._pick(it["names"]) or it["id"]).lower())
    return resultados


def estado(db: GameDB) -> dict:
    """Contrato de /api/status en la web (sin partidas)."""
    return {
        "db": {"built_at": db.built_at,
               "stats": db.stats,
               "sources": db.data.get("sources") or {}},
        "saves": [], "server_time": "", "last_read": "", "error": "",
    }


def detalle_ruta(db: GameDB, url: str) -> dict:
    """Qué debe devolver la ruta en la web, con las mismas reglas que
    server.handle_api() (incluido el 404 de objeto desconocido)."""
    ruta, _, consulta = url.partition("?")
    if ruta == "/api/status":
        return {"result": estado(db)}
    if ruta == "/api/search":
        q = (urllib.parse.parse_qs(consulta).get("q") or [""])[0]
        return {"result": {"results": db.search(q)}}
    if ruta.startswith("/api/item/"):
        pid = urllib.parse.unquote(ruta.split("/api/item/", 1)[1])
        ficha = db.detail(pid)
        if not ficha.get("names") and not ficha.get("icon"):
            return {"error": f"Objeto desconocido: {pid}"}
        return {"result": ficha}
    if ruta == "/api/craftable":
        kind = (urllib.parse.parse_qs(consulta).get("kind") or ["craft"])[0]
        if kind not in ("craft", "refine"):
            kind = "craft"
        return {"result": {"kind": kind, "results": craftable_todas(db, kind)}}
    if ruta.startswith("/api/plan/"):
        pid = urllib.parse.unquote(ruta.split("/api/plan/", 1)[1])
        crudo = (urllib.parse.parse_qs(consulta).get("n") or ["1"])[0]
        try:
            qty = int(crudo or 1)
        except ValueError:
            qty = 1
        return {"result": db.plan(pid, qty, {})}
    raise AssertionError(f"ruta sin definir en la prueba: {url}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compara web/static-db.js con nms_helper/db.py")
    parser.add_argument("--require-node", action="store_true",
                        help="si no hay node, falla (para CI)")
    parser.add_argument("--db", default=str(ROOT / "data" / "db.json"),
                        help="db.json que prueba la web")
    parser.add_argument("--dump-casos", metavar="FICHERO",
                        help="escribe los casos con los resultados de Python "
                             "y sale (para probar la web en un navegador "
                             "sin tener node)")
    args = parser.parse_args()

    db = GameDB(Path(args.db))
    if len(db.items) < 1000:
        print(f"FALLO: solo {len(db.items)} objetos en {args.db}",
              file=sys.stderr)
        return 1

    # Muestrario variado: receta propia, ingrediente de fabricación,
    # sustancia que se recoge, producto que sale refinando, módulo con clase,
    # ingrediente de refinado y un objeto inexistente.
    ids = ["CASING", "LAND1", "FUEL1", "NOEXISTE_ZZZ"]
    ids.append(next(k for k, item in db.items.items() if item.get("class")))
    ids.append(next(pid for pid in db._refine_out if pid not in ids))
    ids.append(next(pid for pid in db._refine_in if pid not in ids))
    ids.append(next(pid for pid in db._craft_in if pid not in ids))
    # producto cuyo plan tiene que pasar por la refinadora (sin receta de
    # fabricación): es la rama que db.plan() dedica al refino
    refino = next(pid for pid in db._refine_out
                  if pid not in db.crafting and pid not in ids)
    ids.append(refino)
    ids = list(dict.fromkeys(ids))          # sin duplicados, mismo orden

    planes = [list(entrada) for entrada in PLANES]
    planes.append([refino, 2])              # plan que pasa por la refinadora

    casos = {
        "search": BUSQUEDAS,
        "detail": ids,
        "craftable": ["craft", "refine"],
        "plan": planes,
        "rutas": RUTAS,
        "esperado": {
            "search": {q: db.search(q) for q in BUSQUEDAS},
            "detail": {pid: db.detail(pid) for pid in ids},
            "craftable": {kind: craftable_todas(db, kind)
                          for kind in ("craft", "refine")},
            "plan": {f"{pid}|{qty}": db.plan(pid, qty, {})
                     for pid, qty in planes},
            "rutas": {ruta: detalle_ruta(db, ruta) for ruta in RUTAS},
            "estado": estado(db),
        },
    }

    if args.dump_casos:
        destino_casos = Path(args.dump_casos)
        destino_casos.parent.mkdir(parents=True, exist_ok=True)
        destino_casos.write_text(
            json.dumps(casos, ensure_ascii=False), encoding="utf-8")
        print(f"Casos con los resultados de Python en {destino_casos}")
        return 0

    node = shutil.which("node")
    if not node:
        if args.require_node:
            print("FALLO: hace falta node para la prueba de paridad "
                  "(Actions lo trae instalado).", file=sys.stderr)
            return 1
        print("  --    paridad web/Python: sin node aquí, se omite "
              "(Actions la ejecuta con --require-node)")
        return 0

    with tempfile.TemporaryDirectory() as carpeta:
        casos_path = Path(carpeta) / "casos.json"
        casos_path.write_text(json.dumps(casos, ensure_ascii=False),
                              encoding="utf-8")
        print("Paridad web/Python: static-db.js frente a db.py")
        proceso = subprocess.run(
            [node, str(ROOT / "tools" / "static_parity.js"),
             str(casos_path), str(Path(args.db))],
            cwd=str(ROOT))
    if proceso.returncode != 0:
        print("FALLA LA PARIDAD ENTRE LA WEB Y PYTHON", file=sys.stderr)
        return proceso.returncode
    print("La API estática cuadra con nms_helper/db.py.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
