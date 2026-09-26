"""Inventario auxiliar: qué guarda el juego sobre tecnología dañada.

Mira el DamageFactor real de tu partida: rango, cuántos huecos por encima
del umbral que usa la interfaz y de qué tipo son.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from nms_helper import save as save_mod  # noqa: E402
from nms_helper.paths import KEYMAP_PATH  # noqa: E402

partidas = save_mod.find_saves()
if not partidas:
    print("no hay partidas")
    sys.exit(0)

keymap = save_mod.load_keymap(KEYMAP_PATH)
data = save_mod.parse_save(partidas[0], keymap)

todos = [(inv.key, s) for inv in data.inventories for s in inv.slots]
valores = sorted({round(s.damage, 4) for _, s in todos})
print(f"partida: {partidas[0].name}  huecos: {len(todos)}")
print(f"valores distintos de DamageFactor: {valores}")

umbral = 0.5
rojos = [(k, s) for k, s in todos if s.damage > umbral]
print(f"\n> damage > {umbral} (lo que la interfaz pinta de rojo): {len(rojos)}")
for k, s in rojos[:20]:
    print(f"   {k:32s} {s.id:32s} damage={s.damage:.3f} tipo={s.kind}")

medio = [(k, s) for k, s in todos if 0 < s.damage <= umbral]
print(f"\n0 < damage <= {umbral} (ni rojos ni sanos): {len(medio)}")
for k, s in medio[:10]:
    print(f"   {k:32s} {s.id:32s} damage={s.damage:.3f} tipo={s.kind}")

print("\ndesglose por tipo de inventario:")
por_tipo = {}
for k, s in todos:
    por_tipo.setdefault(s.kind or "(sin tipo)", [0, 0])
    por_tipo[s.kind or "(sin tipo)"][0] += 1
    if s.damage > umbral:
        por_tipo[s.kind or "(sin tipo)"][1] += 1
for tipo, (total, n) in sorted(por_tipo.items()):
    print(f"   {tipo:24s} {total:5d} huecos, {n} rojos")

# ¿qué otros campos del JSON hablan de daño o reparación?
bruto = json.dumps(json.loads(partidas[0].read_bytes().decode("utf-8", "replace")
                              .replace("\x00", "")) if False else {}, ensure_ascii=False)
raw = partidas[0].read_bytes()
texto = raw.decode("utf-8", "ignore")
claves = sorted(set(re.findall(r'"([A-Za-z_]*(?:Damage|Broken|Repair|Degrad)\w*)"', texto)))
print("\nclaves con Damage/Broken/Repair/Degrad en el JSON:", claves)

# ¿qué hace el juego con DamageFactor en los casos sanos?
print("\nejemplos de DamageFactor por tipo de elemento:")
muestra = {}
for k, s in todos:
    clave = ("tecnología" if s.kind == "Technology" else "objeto")
    muestra.setdefault(clave, []).append(s.damage)
for clave, vals in muestra.items():
    print(f"   {clave:14s} min={min(vals):.3f} max={max(vals):.3f} "
          f"distintos={sorted(set(round(v, 4) for v in vals))[:8]}")
