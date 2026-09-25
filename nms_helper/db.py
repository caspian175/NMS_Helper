"""Carga y consulta la base de datos de objetos y recetas (data/db.json)."""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

from .paths import DATA_DIR


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower()
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def base_id(item_id: str) -> str:
    """'^UP_JET2#38715' -> 'UP_JET2'  |  '^FUEL1' -> 'FUEL1'"""
    return item_id.lstrip("^").split("#")[0]


def unknown_id(item_id: str) -> bool:
    """True si el id del save no es un id de objeto válido.

    En el save aparecen un par de ranuras con bytes que no son UTF-8 válido
    (p. ej. un id procedural corrupto); se conservan tal cual para no perder
    la ranura, pero se marcan como desconocidos para no intentar buscarlos."""
    base = base_id(item_id)
    return not base or re.fullmatch(r"[A-Za-z0-9_]+", base) is None


class GameDB:
    def __init__(self, path: Path | None = None):
        self.path = path or (DATA_DIR / "db.json")
        self.data: dict = {}
        # Iconos descargados a data/icons/: id -> ruta local, y el remoto que
        # tenía cada uno para poder volver atrás.
        self._icon_local: dict[str, str] = {}
        self._icon_remote: dict[str, str] = {}
        self.reload()

    # ------------------------------------------------------------------
    def reload(self) -> None:
        try:
            self._mtime = self.path.stat().st_mtime
        except OSError:
            self._mtime = 0.0
        self.data = json.loads(self.path.read_text(encoding="utf-8"))
        self.items: dict[str, dict] = self.data.get("items", {})
        self.crafting: dict[str, dict] = self.data.get("crafting", {})
        self.refining: list[dict] = self.data.get("refining", [])

        # índices de búsqueda y relaciones
        self._search_index: list[tuple[str, str, str]] = []
        self._by_assistant: dict[str, str] = {}
        for item_id, item in self.items.items():
            names = item.get("name", {})
            en = names.get("en", "")
            es = names.get("es", "")
            for name in (en, es):
                if name:
                    self._search_index.append((normalize(name), item_id, name))
            if item.get("assistant_id"):
                self._by_assistant[item["assistant_id"]] = item_id

        self._refine_out: dict[str, list[dict]] = {}
        self._refine_in: dict[str, list[dict]] = {}
        for index, recipe in enumerate(self.refining):
            self._refine_out.setdefault(recipe["out"]["id"], []).append(index)
            for ing in recipe["in"]:
                self._refine_in.setdefault(ing["id"], []).append(index)

        self._craft_in: dict[str, list[str]] = {}
        for product, recipe in self.crafting.items():
            for ing in recipe["in"]:
                self._craft_in.setdefault(ing["id"], []).append(product)

        # Los iconos descargados a data/icons/ mandan sobre los remotos: se
        # reaplican porque `reload()` deja los objetos como estaban en disco.
        self._apply_icons()

    def fresh(self) -> None:
        """Recarga si data/db.json ha cambiado en disco (p. ej. tras
        ejecutar tools/update_db.py), sin reiniciar el servidor."""
        try:
            mtime = self.path.stat().st_mtime
        except OSError:
            return
        if mtime != self._mtime:
            self.reload()

    # ------------------------------------------------------------------
    def set_icons(self, mapping: dict[str, str]) -> int:
        """Apunta el icono de los objetos indicados a la copia local.

        `mapping` va de id de objeto a ruta local (`/icons/…`). Lo que quede
        fuera recupera su URL original, así que borrar el mapa de iconos
        devuelve el catálogo al estado anterior.
        """
        self._icon_local = dict(mapping or {})
        return self._apply_icons()

    def _apply_icons(self) -> int:
        for item_id, original in self._icon_remote.items():
            item = self.items.get(item_id)
            if item and item.get("icon") != original:
                item["icon"] = original
        applied = 0
        for item_id, local in self._icon_local.items():
            item = self.items.get(item_id)
            if not item or not local:
                continue
            self._icon_remote.setdefault(item_id, item.get("icon", ""))
            item["icon"] = local
            applied += 1
        return applied

    @property
    def stats(self) -> dict:
        self.fresh()
        return self.data.get("stats", {})

    @property
    def built_at(self) -> str:
        self.fresh()
        return self.data.get("built_at", "")

    # ------------------------------------------------------------------
    def get(self, item_id: str) -> dict | None:
        self.fresh()
        return self.items.get(base_id(item_id))

    def label(self, item_id: str, lang: str = "es") -> str:
        self.fresh()
        names = self._names(item_id)
        return names.get(lang) or names.get("en") or names.get("es") \
            or base_id(item_id)

    def _names(self, item_id: str) -> dict:
        item = self.items.get(base_id(item_id), {})
        return item.get("name", {})

    def _named(self, item_id: str) -> dict:
        return {"id": base_id(item_id), "names": self._names(item_id)}

    # ------------------------------------------------------------------
    def search(self, query: str, limit: int = 40) -> list[dict]:
        self.fresh()
        query = normalize(query)
        if not query:
            return []
        starts: list[dict] = []
        contains: list[dict] = []
        seen: set[str] = set()
        for normalized, item_id, _name in self._search_index:
            if item_id in seen:
                continue
            if normalized.startswith(query):
                bucket = starts
            elif query in normalized:
                bucket = contains
            else:
                continue
            seen.add(item_id)
            bucket.append(self._summary(item_id))
            if len(starts) >= limit:
                break
        results = (starts + contains)[:limit]
        results.sort(key=lambda item: self._pick(item["names"]).lower())
        return results

    @staticmethod
    def _pick(names: dict) -> str:
        return names.get("es") or names.get("en") or ""

    def _summary(self, item_id: str) -> dict:
        item_id = base_id(item_id)
        item = self.items.get(item_id, {"id": item_id})
        # formas de conseguir el objeto: se muestran junto a los resultados
        obtain = []
        if item_id in self.crafting:
            obtain.append("craft")
        if self._refine_out.get(item_id):
            obtain.append("refine")
        if not obtain and item.get("type") == "Substance":
            obtain.append("gather")
        return {
            "id": item_id,
            "names": item.get("name", {}),
            "type": item.get("type", ""),
            "symbol": item.get("symbol", ""),
            "color": item.get("color", ""),
            "icon": item.get("icon", ""),
            "class": item.get("class", ""),
            "obtain": obtain,
            "used_in": len(self._craft_in.get(item_id, [])),
        }

    # ------------------------------------------------------------------
    def detail(self, item_id: str) -> dict:
        self.fresh()
        item_id = base_id(item_id)
        item = self.items.get(item_id, {"id": item_id})
        craft = self.crafting.get(item_id)
        refine_out = [self.refining[i] for i in self._refine_out.get(item_id, [])]
        refine_in = [self.refining[i] for i in self._refine_in.get(item_id, [])]
        return {
            "id": item_id,
            "names": item.get("name", {}),
            "descs": item.get("desc", {}),
            "type": item.get("type", ""),
            "kind": item.get("kind", ""),
            "group": item.get("group", ""),
            "symbol": item.get("symbol", ""),
            "color": item.get("color", ""),
            "icon": item.get("icon", ""),
            "class": item.get("class", ""),
            "stack": item.get("stack"),
            "value": item.get("value"),
            "craft": self._recipe_view(craft) if craft else None,
            "refine_out": [self._refine_view(r) for r in refine_out],
            "refine_in": [self._refine_view(r) for r in refine_in],
            "used_in": [self._summary(product)
                        for product in self._craft_in.get(item_id, [])][:30],
        }

    def _recipe_view(self, recipe: dict) -> dict:
        return {
            "out": recipe.get("out", 1),
            "in": [dict(ing, **{"names": self._names(ing["id"])})
                   for ing in recipe["in"]],
        }

    def _refine_view(self, recipe: dict) -> dict:
        return {
            "out": dict(recipe["out"],
                        **{"names": self._names(recipe["out"]["id"])}),
            "in": [dict(ing, **{"names": self._names(ing["id"])})
                   for ing in recipe["in"]],
            "time": recipe.get("time", 0),
            "op": recipe.get("op", ""),
            "op_es": recipe.get("op_es", ""),
        }

    # ------------------------------------------------------------------
    # Fase 1 — planificación de crafteo a partir del inventario real.
    def _times(self, inputs: list[dict], totals: dict) -> int:
        """Cuantas veces se puede ejecutar una receta con lo que hay."""
        times: int | None = None
        for ing in inputs:
            need = int(ing.get("amount", ing.get("n", 1)) or 1)
            have = int(totals.get(ing["id"], 0) or 0)
            if need <= 0:
                continue
            possible = have // need
            times = possible if times is None else min(times, possible)
        return int(times or 0)

    def craftable(self, totals: dict, kind: str = "craft") -> list[dict]:
        """Recetas que se pueden ejecutar ahora con el inventario actual."""
        self.fresh()
        results: list[dict] = []
        if kind == "refine":
            recipes = [{"product": r["out"]["id"], "recipe": r, "out":
                        int(r["out"].get("amount", 1) or 1)} for r in self.refining]
        else:
            recipes = [{"product": pid, "recipe": r,
                        "out": int(r.get("out", 1) or 1)}
                       for pid, r in self.crafting.items()]
        for entry in recipes:
            recipe = entry["recipe"]
            times = self._times(recipe["in"], totals)
            if times <= 0:
                continue
            summary = self._summary(entry["product"])
            summary.update({
                "times": times,
                "out": entry["out"],
                "need": [dict(ing, **{"names": self._names(ing["id"])})
                         for ing in recipe["in"]],
            })
            if kind == "refine":
                summary.update({
                    "time": recipe.get("time", 0),
                    "op": recipe.get("op", ""),
                    "op_es": recipe.get("op_es", ""),
                })
            results.append(summary)
        results.sort(key=lambda item: (self._pick(item["names"]) or item["id"]).lower())
        return results

    def _refine_recipe(self, product_id: str, totals: dict) -> dict | None:
        """Refinadora que más cerca está de poderse ejecutar ya."""
        best = None
        best_ratio = -1.0
        for index in self._refine_out.get(product_id, [])[:6]:
            recipe = self.refining[index]
            ratio = 0.0
            for ing in recipe["in"]:
                need = int(ing.get("amount", ing.get("n", 1)) or 1)
                have = int(totals.get(ing["id"], 0) or 0)
                ratio += min(1.0, have / need) if need else 1.0
            ratio /= max(1, len(recipe["in"]))
            if ratio > best_ratio:
                best, best_ratio = recipe, ratio
        return best

    def plan(self, item_id: str, qty: int, totals: dict,
             max_depth: int = 6) -> dict:
        """Árbol de ingredientes para conseguir 'qty' unidades de un objeto.

        Expande primero la receta de fabricación; si no la tiene, la de
        refinado. Las hojas sin receta y sin material son lo que falta."""
        self.fresh()
        qty = max(1, int(qty or 1))

        def node(pid: str, need: int, seen: set, depth: int) -> dict:
            pid = base_id(pid)
            have = int(totals.get(pid, 0) or 0)
            result = {
                "id": pid,
                "names": self._names(pid),
                "need": need,
                "have": have,
                "missing": max(0, need - have),
                "via": "",
                "children": [],
            }
            if have >= need:
                return result
            if pid in seen or depth >= max_depth:
                return result

            recipe = self.crafting.get(pid)
            if recipe:
                out_per = int(recipe.get("out", 1) or 1)
                batches = -(-need // out_per)          # techo
                result.update(via="craft", batches=batches, out=out_per,
                              children=[node(ing["id"], batches * int(ing.get("amount", ing.get("n", 1)) or 1),
                                             seen | {pid}, depth + 1)
                                        for ing in recipe["in"]])
                return result

            refine = self._refine_recipe(pid, totals)
            if refine:
                out_per = int(refine["out"].get("amount", 1) or 1)
                batches = -(-need // out_per)
                result.update(via="refine", batches=batches, out=out_per,
                              time=refine.get("time", 0),
                              op=refine.get("op", ""), op_es=refine.get("op_es", ""),
                              children=[node(ing["id"], batches * int(ing.get("amount", ing.get("n", 1)) or 1),
                                             seen | {pid}, depth + 1)
                                        for ing in refine["in"]])
            return result

        tree = node(item_id, qty, set(), 0)

        # Lista plana de lo que hay que conseguir (hojas con material faltante)
        shopping: dict[str, int] = {}

        def collect(item: dict) -> None:
            if item["children"]:
                for child in item["children"]:
                    collect(child)
            elif item["missing"] > 0:
                shopping[item["id"]] = shopping.get(item["id"], 0) + item["missing"]

        collect(tree)
        return {
            "root": tree,
            "shopping": [{"id": pid, "names": self._names(pid), "need": amount}
                         for pid, amount in sorted(shopping.items())],
        }


_db: GameDB | None = None


def get_db() -> GameDB:
    global _db
    if _db is None:
        _db = GameDB()
    return _db
