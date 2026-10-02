/* API estática de la web publicada (GitHub Pages).
 *
 * En el programa local, web/app.js pregunta a /api/* y contesta el servidor
 * Python (nms_helper/server.py → nms_helper/db.py). GitHub Pages solo sirve
 * ficheros, así que aquí esas mismas rutas se resuelven en el navegador con
 * data/db.json, replicando las consultas de db.py: búsqueda, ficha de objeto,
 * recetas y plan de crafteo.
 *
 * Al final se exporta createApi() para que tools/static_parity.py pueda
 * enfrentar esta implementación con la de Python (Actions lo comprueba antes
 * de publicar, para que no se descuelgue una de la otra).
 */
"use strict";

/* Utilidades idénticas a nms_helper/db.py ------------------------------- */
function baseId(itemId) {
  // '^UP_JET2#38715' -> 'UP_JET2'  |  '^FUEL1' -> 'FUEL1'
  return String(itemId || "").replace(/^\^+/, "").split("#")[0];
}

function normalize(text) {
  // NFKD → quitar marcas → minúsculas → solo letras y cifras separados por
  // espacios, igual que db.normalize().
  return String(text || "")
    .normalize("NFKD")
    .replace(/\p{M}/gu, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

function amountOf(ing) {
  // int(ing.get("amount", ing.get("n", 1)) or 1)
  const raw = ing && ing.amount !== undefined ? ing.amount
    : ing && ing.n !== undefined ? ing.n : 1;
  return Math.trunc(Number(raw) || 1);
}

function outOf(raw) {
  // int(x or 1): 0 y null también cuentan como 1
  return Math.trunc(Number(raw !== undefined && raw !== null ? raw : 1) || 1);
}

function haveOf(totals, id) {
  return Math.trunc(Number((totals && totals[id]) || 0));
}

function createApi(data) {
  const items = data.items || {};
  const crafting = data.crafting || {};
  const refining = data.refining || [];

  // Índices de relaciones, montados como en db.GameDB.reload().
  const refineOut = {};
  const refineIn = {};
  const craftIn = {};
  for (const [product, recipe] of Object.entries(crafting)) {
    for (const ing of recipe.in || []) {
      (craftIn[ing.id] = craftIn[ing.id] || []).push(product);
    }
  }
  refining.forEach((recipe, index) => {
    (refineOut[recipe.out.id] = refineOut[recipe.out.id] || []).push(index);
    for (const ing of recipe.in || []) {
      (refineIn[ing.id] = refineIn[ing.id] || []).push(index);
    }
  });

  let searchIndex = null;

  function names(itemId) {
    const item = items[baseId(itemId)];
    return (item && item.name) || {};
  }

  function pick(nameMap) {
    return nameMap.es || nameMap.en || "";
  }

  function buildSearchIndex() {
    searchIndex = [];
    for (const [id, item] of Object.entries(items)) {
      const nameMap = (item && item.name) || {};
      // En db.py, primero el nombre inglés y después el español.
      for (const name of [nameMap.en, nameMap.es]) {
        if (name) searchIndex.push([normalize(name), id]);
      }
    }
  }

  function summary(rawId) {
    const id = baseId(rawId);
    const item = items[id] || { id };
    const obtain = [];
    if (crafting[id]) obtain.push("craft");
    if ((refineOut[id] || []).length) obtain.push("refine");
    if (!obtain.length && item.type === "Substance") obtain.push("gather");
    return {
      id,
      names: item.name || {},
      type: item.type !== undefined ? item.type : "",
      symbol: item.symbol !== undefined ? item.symbol : "",
      color: item.color !== undefined ? item.color : "",
      icon: item.icon !== undefined ? item.icon : "",
      class: item.class !== undefined ? item.class : "",
      obtain,
      used_in: (craftIn[id] || []).length,
    };
  }

  function search(query, limit) {
    limit = limit === undefined ? 40 : limit;
    const wanted = normalize(query);
    if (!wanted) return [];
    if (!searchIndex) buildSearchIndex();
    const starts = [];
    const contains = [];
    const seen = new Set();
    for (const entry of searchIndex) {
      const norm = entry[0];
      const id = entry[1];
      if (seen.has(id)) continue;
      let bucket = null;
      if (norm.startsWith(wanted)) bucket = starts;
      else if (norm.includes(wanted)) bucket = contains;
      else continue;
      seen.add(id);
      bucket.push(summary(id));
      if (starts.length >= limit) break;
    }
    const results = starts.concat(contains).slice(0, limit);
    // Mismo criterio que db.search(): nombre en el idioma actual, a minúsculas.
    results.sort((a, b) => {
      const ka = pick(a.names).toLowerCase();
      const kb = pick(b.names).toLowerCase();
      return ka < kb ? -1 : ka > kb ? 1 : 0;
    });
    return results;
  }

  function recipeView(recipe) {
    return {
      out: recipe.out !== undefined ? recipe.out : 1,
      in: (recipe.in || []).map((ing) => ({ ...ing, names: names(ing.id) })),
    };
  }

  function refineView(recipe) {
    return {
      out: { ...recipe.out, names: names(recipe.out.id) },
      in: (recipe.in || []).map((ing) => ({ ...ing, names: names(ing.id) })),
      time: recipe.time !== undefined ? recipe.time : 0,
      op: recipe.op !== undefined ? recipe.op : "",
      op_es: recipe.op_es !== undefined ? recipe.op_es : "",
    };
  }

  function detail(rawId) {
    const id = baseId(rawId);
    const item = items[id] || { id };
    const craft = crafting[id];
    return {
      id,
      names: item.name || {},
      descs: item.desc !== undefined ? item.desc : {},
      type: item.type !== undefined ? item.type : "",
      kind: item.kind !== undefined ? item.kind : "",
      group: item.group !== undefined ? item.group : "",
      symbol: item.symbol !== undefined ? item.symbol : "",
      color: item.color !== undefined ? item.color : "",
      icon: item.icon !== undefined ? item.icon : "",
      class: item.class !== undefined ? item.class : "",
      stack: item.stack !== undefined ? item.stack : null,
      value: item.value !== undefined ? item.value : null,
      craft: craft ? recipeView(craft) : null,
      refine_out: (refineOut[id] || []).map((i) => refineView(refining[i])),
      refine_in: (refineIn[id] || []).map((i) => refineView(refining[i])),
      used_in: (craftIn[id] || []).map((pid) => summary(pid)).slice(0, 30),
    };
  }

  /* Recetas completas, sin filtrar por existencias: en la web no hay partida,
     así que «lo que puedo hacer ahora» es «todas las recetas» (por eso los
     resultados no llevan `times`, que en el programa local cuenta cuántas
     veces se puede ejecutar con lo que hay). */
  function craftable(totals, kind) {
    const results = [];
    let entries;
    if (kind === "refine") {
      entries = refining.map((recipe) => ({
        product: recipe.out.id, recipe, out: outOf(recipe.out.amount),
      }));
    } else {
      entries = Object.keys(crafting).map((pid) => ({
        product: pid, recipe: crafting[pid], out: outOf(crafting[pid].out),
      }));
    }
    for (const entry of entries) {
      const item = summary(entry.product);
      item.out = entry.out;
      item.need = (entry.recipe.in || [])
        .map((ing) => ({ ...ing, names: names(ing.id) }));
      if (kind === "refine") {
        item.time = entry.recipe.time !== undefined ? entry.recipe.time : 0;
        item.op = entry.recipe.op !== undefined ? entry.recipe.op : "";
        item.op_es = entry.recipe.op_es !== undefined ? entry.recipe.op_es : "";
      }
      results.push(item);
    }
    results.sort((a, b) => {
      const ka = (pick(a.names) || a.id).toLowerCase();
      const kb = (pick(b.names) || b.id).toLowerCase();
      return ka < kb ? -1 : ka > kb ? 1 : 0;
    });
    return results;
  }

  function refineRecipe(pid, totals) {
    // La refinadora más cerca de poderse ejecutar (máx. las 6 primeras).
    const indices = (refineOut[pid] || []).slice(0, 6);
    let best = null;
    let bestRatio = -1;
    for (const index of indices) {
      const recipe = refining[index];
      let ratio = 0;
      for (const ing of recipe.in || []) {
        const need = amountOf(ing);
        const have = haveOf(totals, ing.id);
        ratio += need ? Math.min(1, have / need) : 1;
      }
      ratio /= Math.max(1, (recipe.in || []).length);
      if (ratio > bestRatio) {
        best = recipe;
        bestRatio = ratio;
      }
    }
    return best;
  }

  function plan(rawId, qty, totals) {
    const wanted = Math.max(1, Math.trunc(Number(qty) || 1));
    totals = totals || {};
    const maxDepth = 6;

    function node(rawPid, need, seen, depth) {
      const pid = baseId(rawPid);
      const have = haveOf(totals, pid);
      const result = {
        id: pid,
        names: names(pid),
        need,
        have,
        missing: Math.max(0, need - have),
        via: "",
        children: [],
      };
      if (have >= need) return result;
      if (seen.has(pid) || depth >= maxDepth) return result;

      const recipe = crafting[pid];
      if (recipe) {
        const outPer = outOf(recipe.out);
        const batches = Math.ceil(need / outPer);
        result.via = "craft";
        result.batches = batches;
        result.out = outPer;
        result.children = (recipe.in || []).map((ing) =>
          node(ing.id, batches * amountOf(ing),
            new Set([...seen, pid]), depth + 1));
        return result;
      }

      const refine = refineRecipe(pid, totals);
      if (refine) {
        const outPer = outOf(refine.out.amount);
        const batches = Math.ceil(need / outPer);
        result.via = "refine";
        result.batches = batches;
        result.out = outPer;
        result.time = refine.time !== undefined ? refine.time : 0;
        result.op = refine.op !== undefined ? refine.op : "";
        result.op_es = refine.op_es !== undefined ? refine.op_es : "";
        result.children = (refine.in || []).map((ing) =>
          node(ing.id, batches * amountOf(ing),
            new Set([...seen, pid]), depth + 1));
      }
      return result;
    }

    const tree = node(rawId, wanted, new Set(), 0);

    // Lista plana de lo que hay que conseguir (hojas con material faltante).
    const shopping = {};
    (function collect(item) {
      if (item.children.length) {
        item.children.forEach(collect);
      } else if (item.missing > 0) {
        shopping[item.id] = (shopping[item.id] || 0) + item.missing;
      }
    })(tree);

    return {
      root: tree,
      shopping: Object.keys(shopping).sort().map((pid) => ({
        id: pid, names: names(pid), need: shopping[pid],
      })),
    };
  }

  function status() {
    return {
      db: {
        built_at: data.built_at !== undefined ? data.built_at : "",
        stats: data.stats || {},
        sources: data.sources || {},
      },
      saves: [],
      server_time: "",
      last_read: "",
      error: "",
    };
  }

  /* El mismo enrutado que server.handle_api(), en miniatura: solo las rutas
     que la interfaz usa sin partida. */
  async function handle(url) {
    const cut = url.indexOf("?");
    const path = cut < 0 ? url : url.slice(0, cut);
    const query = new URLSearchParams(cut < 0 ? "" : url.slice(cut + 1));

    if (path === "/api/status") return status();
    if (path === "/api/search") {
      return { results: search(query.get("q") || "") };
    }
    if (path.startsWith("/api/item/")) {
      const id = decodeURIComponent(path.slice("/api/item/".length));
      const item = detail(id);
      // server.py responde 404 si no hay ni nombre ni icono.
      if (!Object.keys(item.names).length && !item.icon) {
        throw new Error(`Objeto desconocido: ${id}`);
      }
      return item;
    }
    if (path === "/api/craftable") {
      const kind = query.get("kind") === "refine" ? "refine" : "craft";
      return { kind, results: craftable({}, kind) };
    }
    if (path.startsWith("/api/plan/")) {
      const id = decodeURIComponent(path.slice("/api/plan/".length));
      // Igual que el servidor: int(...) con "1" por defecto y 1 si no es
      // un entero; la cantidad mínima la fija plan().
      const raw = (query.get("n") || "1").trim();
      const qty = /^[+-]?\d+$/.test(raw) ? parseInt(raw, 10) : 1;
      return plan(id, qty, {});
    }
    throw new Error(`Ruta desconocida: ${path}`);
  }

  return { data, search, detail, craftable, plan, status, handle };
}

/* Node (tools/static_parity.js) necesita createApi; en el navegador solo
   interesa arrancar la API si estamos en el sitio estático. */
if (typeof module !== "undefined" && module.exports) {
  module.exports = { createApi, normalize, baseId };
}

if (typeof window !== "undefined" && window.NMS_STATIC === true) {
  const loader = fetch("data/db.json").then((res) => {
    if (!res.ok) throw new Error(`data/db.json (${res.status})`);
    return res.json();
  }).then((dbData) => createApi(dbData));

  window.NMS_STATIC_API = {
    ready: loader,
    get: (url) => loader.then((api) => api.handle(url)),
  };
}
