"""Inventario auxiliar: qué guarda el juego sobre tecnología dañada.

Mira el DamageFactor real de tu partida: rango, cuántos huecos por encima
del umbral que usa la interfaz y de qué tipo son.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from nms_helper import save  # noqa: E402

partidas = save.find_saves()
if not partidas:
    print("no hay partidas")
    sys.exit(0)

snap = save.load(partidas[0])
invs = snap.inventories

todos = [(k, s) for k, s in invs.items() for s in s.slots]
valores = sorted({round(s.damage, 4) for _, s in todos})
print(f"huecos totales: {len(todos)}")
print(f"valores distintos de DamageFactor: {valores}")

umbral = 0.5
por_encima = [(k, s) for k, s in todos if s.damage > umbral]
print(f"\nhuecos con damage > {umbral} (lo que la interfaz pinta de rojo): {len(por_encima)}")
for k, s in por_encima[:15]:
    print(f"   {k:34s} {s.id:30s} damage={s.damage:.3f} tipo={s.kind}")

print("\nhuecos con 0 < damage <= 0.5 (ni rojos ni sanos):")
medio = [(k, s) for k, s in todos if 0 < s.damage <= umbral]
print(f"   {len(medio)}")
for k, s in medio[:10]:
    print(f"   {k:34s} {s.id:30s} damage={s.damage:.3f}")

# ¿hay campos en el guardado que hablen de reparación o avería?
print("\ncampos del JSON que mencionen daño/reparación/avería:")
import json  # noqa: E402
texto = json.dumps(snap.raw if hasattr(snap, 'raw') else {}, ensure_ascii=False)
if not texto.strip(" {}"):
    bruto = partidas[0].read_text(encoding="utf-8", errors="replace")
else:
    bruto = texto
import re  # noqa: E402
claves = sorted(set(re.findall(r'"(\w*(?:Damage|Broken|Repair|Health)\w*)"', bruto)))
print("  ", claves)
