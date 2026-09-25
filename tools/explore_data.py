"""Explora las fuentes descargadas y mide la cobertura del cruce de nombres."""
import json
import re
import sys
from pathlib import Path

DL = Path("tools/_dl")


def norm(s: str) -> str:
    s = (s or "").lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return s.strip()


def load_assistant(folder: str):
    items = {}
    for f in (DL / "lang" / folder).glob("*.lang.json"):
        if f.name in ("Refinery.lang.json", "All_Lang_Data.json"):
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if not isinstance(data, list):
            continue
        for entry in data:
            if not isinstance(entry, dict) or "Name" not in entry:
                continue
            items[entry.get("Id")] = entry
    return items


def main():
    nm = json.loads((DL / "items_nmstoolkit.json").read_text(encoding="utf-8")) \
        if (DL / "items_nmstoolkit.json").exists() else None
    craft = json.loads((DL / "Crafting_Table.json").read_text(encoding="utf-8"))
    subst = json.loads((DL / "Substance_Table.json").read_text(encoding="utf-8"))
    prod = json.loads((DL / "Product_Table.json").read_text(encoding="utf-8"))
    tech = json.loads((DL / "Technology_Table.json").read_text(encoding="utf-8"))
    refin = json.loads((DL / "Refining_Table.json").read_text(encoding="utf-8"))

    en = load_assistant("en")
    es = load_assistant("es")
    print("assistant en:", len(en), "es:", len(es))
    print("craft:", len(craft), "subst:", len(subst), "prod:", len(prod),
          "tech:", len(tech), "refin:", len(refin))
    if nm is not None:
        print("nmstoolkit:", len(nm))

    en_by_name = {}
    for it in en.values():
        en_by_name.setdefault(norm(it["Name"]), it)
    matched = sum(1 for it in en.values() if norm(it["Name"]) in
                  {norm(x["Name"]) for x in es.values()})
    print("assistant en->es por nombre:", matched, "/", len(en))

    # cobertura: nombres de las tablas Handbook -> Assistant
    missing = []
    total = 0
    for table in (subst, prod, tech):
        for key, entry in table.items():
            name = entry.get("NameLower_Text") or entry.get("Name_Text") or ""
            total += 1
            if norm(name) not in en_by_name:
                missing.append((key, name))
    print("Handbook -> Assistant:", total - len(missing), "/", total)
    print("sin match (muestra):", missing[:25])

    # recetas
    rec = [(k, v.get("Ingredients")) for k, v in craft.items() if v.get("Ingredients")]
    print("recetas de crafteo con ingredientes:", len(rec), rec[:3])
    rcount = sum(len(v.get("Recipes") or []) for v in refin.values())
    print("recetas de refinado:", rcount)


if __name__ == "__main__":
    sys.exit(main())
