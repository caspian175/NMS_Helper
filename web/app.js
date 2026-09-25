/* NMS Helper — interfaz */
"use strict";

const state = {
  lang: localStorage.getItem("nms.lang") || "es",
  view: "inventory",
  snapshot: null,
  invIndex: 0,
  filter: "",
  typeFilter: "all",
  craftKind: "craft",
  planQty: 1,
  status: null,
  detail: null,
  missing: null,
  lastPayload: "",
};

const I18N = {
  es: {
    units: "Unidades", nanites: "Nanitas", quicksilver: "Mercurio",
    tab_inventory: "Inventario", tab_recipes: "Recetas",
    filter: "Filtrar objetos…",
    search: "Busca un objeto: circuito de vuelo, carbono…",
    pick_item: "Elige un objeto para ver cómo se fabrica y se refina.",
    health: "Salud", shield: "Escudo", energy: "Energía",
    ship: "Nave", ammo: "Munición",
    no_save: "No se ha encontrado ninguna partida en %APPDATA%\\HelloGames\\NMS",
    load_error: "Error leyendo la partida",
    loading: "Cargando partida…",
    no_match: "Sin objetos que coincidan con el filtro.",
    no_results: "Sin resultados.",
    craft_title: "Fabricación (fabricador)",
    refine_out_title: "Se obtiene refinando",
    refine_in_title: "Se usa en refinadoras",
    used_in_title: "Se usa para fabricar",
    you_have: "Tienes", need: "Necesitas", missing: "Te faltan",
    stack: "Por pila", value: "Valor", group: "Grupo",
    updated_save: "Partida guardada el", reading: "Leyendo",
    unknown: "Objeto desconocido",
    known: "Receta conocida", unknown_recipe: "Receta no descubierta",
    empty_inv: "Contenedor vacío",
    seconds: "s", save_slot: "Partida", rescan: "Buscar partidas",
    save_latest: "más reciente", save_older: "más antiguo",
    item_class: "Clase",
    no_data: "Sin datos de este objeto en la base de datos.",
    unknown_hint: "La partida guarda este objeto con un id ilegible, así que " +
      "no se puede identificar. Es normal: es un dato interno del guardado.",
    open_item: "Ver detalle del objeto",
    obtain_craft: "Se fabrica",
    obtain_refine: "Se refina",
    obtain_gather: "Se recolecta",
    obtain_used: "Se usa en %s recetas",
    tab_profile: "Partida",
    fleet_ships: "Naves", fleet_tools: "Multiherramientas",
    chip_all: "Todo", chip_substance: "Sustancias",
    chip_product: "Productos", chip_tech: "Tecnología",
    inv_empty: "Sin objetos que coincidan con el filtro.",
    group_suit: "Exotraje", group_ship: "Flota",
    group_freighter: "Carguero", group_multitool: "Multiherramientas",
    group_storage: "Refugio y cajas", group_other: "Otros",
    free_slots: "huecos libres", slots_unit: "huecos",
    state_label: "Ubicación", mode_label: "Modo", time_label: "Tiempo jugado",
    address_label: "Dirección galáctica",
    galaxy_label: "Galaxia", system_label: "Sistema", planet_label: "Planeta",
    copy: "Copiar", copied: "Copiado",
    active_label: "En uso", view_inv: "Ver inventario",
    craftable_btn: "¿Qué puedo hacer ahora?",
    craftable_none: "No puedes fabricar ni refinar nada con lo que llevas encima.",
    tab_craft: "Fabricación", tab_refine: "Refinado",
    goals_btn: "Objetivos",
    goals_empty: "Abre la ficha de un objeto y pulsa «Añadir a objetivos» " +
      "para ver aquí lo que te falta.",
    goal_add: "Añadir a objetivos", goal_remove: "Quitar",
    in_goals: "En objetivos", copy_list: "Copiar lista",
    shopping: "Lista de la compra",
    plan_title: "Plan para conseguirlo", plan_qty: "Cantidad",
    plan_by_craft: "se fabrica", plan_by_refine: "se refina",
    plan_ok: "Alcanzable con lo que tienes",
    cargo_label: "Carga", fleet_empty: "No hay nada guardado aquí.",
    please_wait: "Cargando…",
    db_btn: "Actualizar datos",
    db_title: "Actualizar datos",
    db_hint: "Vuelve a descargar las tablas de la comunidad (recetas, refinado, " +
      "objetos), los textos del juego y los iconos del catálogo. Útil tras un " +
      "parche de No Man's Sky: no toca tus partidas.",
    db_what_all: "Todo (tablas + textos)",
    db_what_tables: "Solo tablas (recetas y objetos)",
    db_what_lang: "Solo textos del juego",
    db_what_icons: "Solo iconos (todo el catálogo)",
    db_start: "Empezar", db_running_label: "En marcha",
    db_idle: "Sin actualizaciones todavía.",
    db_running: "Actualizando… no pares el servidor.",
    db_done: "Terminado: los cambios ya se ven en la interfaz.",
    db_failed: "La actualización ha fallado; mir el log de arriba.",
    db_busy: "Ya hay una actualización en marcha.",
    db_no_update: "No se pudo lanzar la actualización.",
    tab_tools: "Herramientas",
    ley_title: "Líneas ley",
    ley_hint: "Las líneas ley son meridianos por donde salen tres depósitos. " +
      "Apunta tus coordenadas en un punto de referencia, muévete al menos " +
      "1000 u y vuelve a apuntarlas con la distancia recorrida.",
    ley_read1: "Lectura 1", ley_read2: "Lectura 2",
    ley_lat: "Lat", ley_long: "Long",
    ley_dist: "Distancia", ley_units: "u",
    ley_calc: "Calcular",
    ley_bad: "Faltan datos: apunta los dos puntos y la distancia recorrida.",
    ley_same: "Los dos puntos son el mismo: muévete al menos 1000 u.",
    ley_lines_title: "Meridianos candidatos",
    ley_valid: "Válido entre 45°N y 45°S",
    ley_scale: "Escala",
    ley_nav_target: "Línea", ley_nav_pos: "Posición", ley_nav_dist: "Distancia",
    ley_nav_here: "Estás en la línea",
    ley_nav_hint: "Ya estás sobre la línea: sigue al norte o al sur buscando " +
      "los tres depósitos.",
    ley_nav_walk: "Camina en esa dirección hasta la línea y después sigue al " +
      "norte o al sur.",
    ley_dir_east: "Este", ley_dir_west: "Oeste",
    ley_points_title: "Puntos guardados por planeta",
    ley_planet_ph: "Planeta",
    ley_point_ph: "Nombre del punto",
    ley_point_new: "Punto",
    ley_point_add: "Guardar",
    ley_point_empty: "Sin puntos en este planeta.",
    ley_point_bad: "Ponle nombre al planeta y escribe el lat/long del punto.",
    ley_fill1: "Usar como lectura 1", ley_fill2: "Usar como lectura 2",
    ley_point_del: "Borrar punto",
    portal_title: "Dirección de portal",
    portal_hint: "Convierte la dirección galáctica (la que enseña el refuerzo " +
      "de señal) en los 12 glifos con los que marcas un portal, o al revés. " +
      "El primer glifo es el planeta.",
    portal_use_save: "Usar mi dirección",
    portal_to_glyphs: "A glifos",
    portal_to_addr: "A dirección",
    portal_code: "Código de portal",
    portal_breakdown: "planeta · sistema · Y · Z · X",
    portal_bad_addr: "Dirección no válida: usa el formato 046A:0081:0D6D:0038.",
    portal_bad_glyphs: "Hacen falta 12 glifos (del 0 al 9 y de la A a la F).",
    portal_planet_title: "Primer glifo: planeta dentro del sistema",
    profile_glyphs: "Ver glifos",
  },
  en: {
    units: "Units", nanites: "Nanites", quicksilver: "Quicksilver",
    tab_inventory: "Inventory", tab_recipes: "Recipes",
    filter: "Filter items…",
    search: "Search an item: flight circuit, carbon…",
    pick_item: "Pick an item to see how to craft and refine it.",
    health: "Health", shield: "Shield", energy: "Energy",
    ship: "Ship", ammo: "Ammo",
    no_save: "No save found in %APPDATA%\\HelloGames\\NMS",
    load_error: "Error reading the save",
    loading: "Loading save…",
    no_match: "No items match the filter.",
    no_results: "No results.",
    craft_title: "Crafting (fabricator)",
    refine_out_title: "Obtained by refining",
    refine_in_title: "Used in refiners",
    used_in_title: "Used to craft",
    you_have: "You have", need: "Need", missing: "Missing",
    stack: "Stack", value: "Value", group: "Group",
    updated_save: "Save written on", reading: "Reading",
    unknown: "Unknown item",
    known: "Recipe known", unknown_recipe: "Recipe not discovered",
    empty_inv: "Empty container",
    seconds: "s", save_slot: "Save", rescan: "Rescan saves",
    save_latest: "newest", save_older: "older",
    item_class: "Class",
    no_data: "No data for this item in the database.",
    unknown_hint: "The save stores this item with an unreadable id, so it " +
      "cannot be identified. This is normal: it is internal save data.",
    open_item: "Open item details",
    obtain_craft: "Crafted",
    obtain_refine: "Refined",
    obtain_gather: "Gathered",
    obtain_used: "Used in %s recipes",
    tab_profile: "Profile",
    fleet_ships: "Ships", fleet_tools: "Multi-tools",
    chip_all: "All", chip_substance: "Substances",
    chip_product: "Products", chip_tech: "Technology",
    inv_empty: "No items match the filter.",
    group_suit: "Exosuit", group_ship: "Fleet",
    group_freighter: "Freighter", group_multitool: "Multi-tools",
    group_storage: "Base & storage", group_other: "Other",
    free_slots: "free slots", slots_unit: "slots",
    state_label: "Location", mode_label: "Mode", time_label: "Play time",
    address_label: "Galactic address",
    galaxy_label: "Galaxy", system_label: "System", planet_label: "Planet",
    copy: "Copy", copied: "Copied",
    active_label: "Equipped", view_inv: "Open inventory",
    craftable_btn: "What can I make now?",
    craftable_none: "You cannot craft or refine anything with what you carry.",
    tab_craft: "Crafting", tab_refine: "Refining",
    goals_btn: "Goals",
    goals_empty: "Open an item page and press “Add to goals” to see here " +
      "what you are missing.",
    goal_add: "Add to goals", goal_remove: "Remove",
    in_goals: "In goals", copy_list: "Copy list",
    shopping: "Shopping list",
    plan_title: "Plan to get it", plan_qty: "Quantity",
    plan_by_craft: "crafted", plan_by_refine: "refined",
    plan_ok: "Reachable with what you have",
    cargo_label: "Cargo", fleet_empty: "Nothing stored here.",
    please_wait: "Loading…",
    db_btn: "Update data",
    db_title: "Update data",
    db_hint: "Re-downloads the community tables (crafting, refining, items), " +
      "the game texts and the catalogue icons. Useful after a No Man's Sky " +
      "patch: it never touches your saves.",
    db_what_all: "Everything (tables + texts)",
    db_what_tables: "Tables only (recipes and items)",
    db_what_lang: "Game texts only",
    db_what_icons: "Icons only (whole catalogue)",
    db_start: "Start", db_running_label: "Running",
    db_idle: "No updates yet.",
    db_running: "Updating… don't stop the server.",
    db_done: "Done: the changes are already in the interface.",
    db_failed: "The update failed; check the log above.",
    db_busy: "An update is already running.",
    db_no_update: "Could not start the update.",
    tab_tools: "Tools",
    ley_title: "Ley lines",
    ley_hint: "Ley lines are meridians where three deposits spawn. Note your " +
      "coordinates at a reference point, move at least 1000 u and take a " +
      "second reading with the distance travelled.",
    ley_read1: "Reading 1", ley_read2: "Reading 2",
    ley_lat: "Lat", ley_long: "Long",
    ley_dist: "Distance", ley_units: "u",
    ley_calc: "Calculate",
    ley_bad: "Missing data: enter both points and the distance travelled.",
    ley_same: "Both points are the same: move at least 1000 u.",
    ley_lines_title: "Candidate meridians",
    ley_valid: "Valid between 45°N and 45°S",
    ley_scale: "Scale",
    ley_nav_target: "Line", ley_nav_pos: "Position", ley_nav_dist: "Distance",
    ley_nav_here: "You are on the line",
    ley_nav_hint: "You are on the line: keep going north or south to find " +
      "the three deposits.",
    ley_nav_walk: "Walk that way to the line and then head north or south.",
    ley_dir_east: "East", ley_dir_west: "West",
    ley_points_title: "Points saved per planet",
    ley_planet_ph: "Planet",
    ley_point_ph: "Point name",
    ley_point_new: "Point",
    ley_point_add: "Save",
    ley_point_empty: "No points on this planet.",
    ley_point_bad: "Name the planet and type the point's lat/long.",
    ley_fill1: "Use as reading 1", ley_fill2: "Use as reading 2",
    ley_point_del: "Delete point",
    portal_title: "Portal address",
    portal_hint: "Turns a galactic address (the one the signal booster shows) " +
      "into the 12 glyphs you dial on a portal, and back. The first glyph is " +
      "the planet.",
    portal_use_save: "Use my address",
    portal_to_glyphs: "To glyphs",
    portal_to_addr: "To address",
    portal_code: "Portal code",
    portal_breakdown: "planet · system · Y · Z · X",
    portal_bad_addr: "Invalid address: use the format 046A:0081:0D6D:0038.",
    portal_bad_glyphs: "You need 12 glyphs (0-9 and A-F).",
    portal_planet_title: "First glyph: planet within the system",
    profile_glyphs: "See glyphs",
  },
};

const t = (key) => (I18N[state.lang] && I18N[state.lang][key]) || key;
const nameOf = (names) => (names && (names[state.lang] || names.en || names.es)) || "";
const altOf = (names) => (names && (state.lang === "es" ? names.en : names.es)) || "";
const $ = (sel) => document.querySelector(sel);

/* Clase/rango de los módulos de tecnología. Los colores son los que usa el
   propio juego en sus iconos de módulo (proctech.c/b/a/s/x.*): C verde,
   B azul, A rosa, S dorado, X morado y "?" gris (oxidado/anómalo). */
const CLASS_COLORS = {
  C: "#40AF72", B: "#358CCC", A: "#CD6AB1", S: "#DC9E32",
  X: "#7E5DE4", "?": "#9BA1A8",
};
const classColor = (cls) => CLASS_COLORS[cls] || CLASS_COLORS["?"];
// Espejo del validador del servidor: ids con bytes ilegibles en el save.
const isUnknownId = (id) => {
  const base = String(id || "").replace(/^\^/, "").split("#")[0];
  return !/^[A-Za-z0-9_]+$/.test(base);
};

/* ------------------------------------------------------------------ i18n */
function applyI18n() {
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = t(el.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-ph]").forEach((el) => {
    el.placeholder = t(el.dataset.i18nPh);
  });
  $("#lang-toggle").textContent = state.lang === "es" ? "EN" : "ES";
  document.documentElement.lang = state.lang;
}

/* --------------------------------------------------------------- helpers */
async function getJSON(url) {
  const res = await fetch(url);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || res.statusText);
  return data;
}

function fmtNumber(value) {
  return new Intl.NumberFormat(state.lang === "es" ? "es-ES" : "en-US").format(value || 0);
}

/* Texto seguro para incrustar en un manejador inline dentro de un atributo
   HTML (una comilla o una barra invertida dejarían el onerror sin instalar
   y la imagen rota se quedaría visible). */
function jsq(value) {
  return String(value)
    .replace(/\\/g, "\\\\")
    .replace(/'/g, "\\'")
    .replace(/"/g, "&quot;")
    .replace(/\s+/g, " ")
    .trim();
}

function thumb(item, size) {
  const color = item.color && /^[0-9A-Fa-f]{6}$/.test(item.color) ? "#" + item.color : "#4fd1e0";
  const label = (item.symbol || (item.names ? nameOf(item.names) : item.name || "?").slice(0, 2));
  const cls = size === "big" ? "big-fallback" : size === "thumb" ? "thumb-fallback" : "fallback";
  if (item.icon) {
    // onerror va antes de src: si la imagen falla al cargar, el gestor ya
    // está instalado y el hueco se sustituye por el icono de respaldo.
    return `<img class="${size === "big" ? "" : size === "thumb" ? "thumb" : ""}"
      onerror="this.outerHTML='<span class=\\'${cls}\\' style=\\'background:${color}\\'>${jsq(label)}</span>'"
      src="${item.icon}" alt="">`;
  }
  return `<span class="${cls}" style="background:${color}">${escapeHtml(label)}</span>`;
}

/* --------------------------------------------------------------- estado */
async function loadStatus() {
  try {
    state.status = await getJSON("/api/status");
    renderSaveSelect();
    const stats = state.status.db.stats || {};
    $("#last-read").textContent =
      `${state.status.db.built_at || ""} · ${stats.items || 0} objetos · ` +
      `${(stats.crafting_recipes || 0) + (stats.refining_recipes || 0)} recetas`;
    setDot(state.status.error ? "error" : "");
  } catch (err) {
    setDot("error");
  }
}

function renderSaveSelect() {
  const select = $("#save-select");
  const saves = (state.status && state.status.saves) || [];
  if (!saves.length) {
    select.innerHTML = `<option>${t("no_save")}</option>`;
    return;
  }
  // El juego escribe dos ficheros por partida (un autosave y un punto de
  // restauración): save.hg + save2.hg. Se agrupan en "Partida 1", "Partida 2"…
  // y se indica cuál de los dos es el que se escribió de último.
  const groups = new Map();
  saves.forEach((s) => {
    const pair = s.pair || 0;
    if (!groups.has(pair)) groups.set(pair, []);
    groups.get(pair).push(s);
  });
  const html = [];
  [...groups.entries()].sort((a, b) => a[0] - b[0]).forEach(([pair, list]) => {
    const label = pair > 0 ? `${t("save_slot")} ${pair}` : t("save_slot");
    html.push(`<optgroup label="${escapeAttr(label)}">`);
    list.forEach((s) => {
      const role = list.length > 1
        ? `${s.newest ? t("save_latest") : t("save_older")} · `
        : "";
      html.push(
        `<option value="${s.index}" ${s.active ? "selected" : ""}>` +
        `${escapeHtml(role + s.modified + " · " + s.file)}</option>`);
    });
    html.push("</optgroup>");
  });
  select.innerHTML = html.join("");
}

function setDot(mode) {
  const dot = $("#live-dot");
  dot.className = "dot" + (mode ? " " + mode : "");
}

async function loadInventory() {
  setDot("busy");
  try {
    const payload = await getJSON("/api/inventory");
    const text = JSON.stringify(payload);
    if (text !== state.lastPayload) {
      state.lastPayload = text;
      state.snapshot = payload;
      if (payload.catalog) {
        db.remember(Object.entries(payload.catalog).map(([id, info]) => ({ id, ...info })));
      }
      renderHeader();
      renderVitals();
      renderInvList();
      renderInvGrid();
      renderProfile();
      updateGoalsCount();
      if (state.detail) renderDetail(state.detail.id, true);
    }
    setDot("");
  } catch (err) {
    setDot("error");
    $("#save-meta").textContent = `${t("load_error")}: ${err.message}`;
  }
}

/* ------------------------------------------------------------- cabecera */
function renderHeader() {
  const s = state.snapshot;
  if (!s) return;
  const save = s.save;
  const time = save.play_time
    ? ` · ${Math.floor(save.play_time / 3600)}h ${Math.floor((save.play_time % 3600) / 60)}m`
    : "";
  $("#save-meta").textContent =
    [save.name || save.summary || save.file, save.mode, `${t("updated_save")} ${save.updated}${time}`]
      .filter(Boolean).join(" · ");
  $("#w-units").textContent = fmtNumber(s.wallet.units);
  $("#w-nanites").textContent = fmtNumber(s.wallet.nanites);
  $("#w-quicksilver").textContent = fmtNumber(s.wallet.quicksilver);
}

function renderVitals() {
  const v = state.snapshot && state.snapshot.vitals;
  if (!v) { $("#vitals").innerHTML = ""; return; }

  const bars = [
    [t("health"), v.health],
    [t("shield"), v.shield],
    [t("energy"), v.energy],
  ];
  const html = bars.map(([label, value]) => {
    const pct = Math.max(0, Math.min(100, value || 0));
    return `<div class="vital ${pct < 30 ? "low" : ""}">
      <div class="v-label"><span>${label}</span><span>${pct}%</span></div>
      <div class="bar"><i style="width:${pct}%"></i></div>
    </div>`;
  });

  html.push(`<div class="vital">
    <div class="v-label"><span>${t("ship")}</span></div>
    <div class="ammo">
      <span>♥ ${fmtNumber(v.ship_health)}</span> ·
      <span>⛨ ${fmtNumber(v.ship_shield)}</span>
    </div>
  </div>`);

  const ammo = Object.entries(v.ammo || {})
    .map(([label, qty]) => `<span>${label}: <b>${fmtNumber(qty)}</b></span>`)
    .join(" · ");
  html.push(`<div class="vital">
    <div class="v-label"><span>${t("ammo")}</span></div>
    <div class="ammo">${ammo}</div>
  </div>`);

  $("#vitals").innerHTML = html.join("");
}

/* ------------------------------------------------------------ inventario */
// Las etiquetas de sección llegan del lector de la partida (en español);
// aquí se vuelven a inglés para que el conmutador de idioma sea completo.
const SECTION_EN = [
  ["Contenedor de refugio ", "Storage container "],
  ["Contenedor de exóticos", "Colossal archive"],
  ["Cohetes del exotraje", "Exosuit rocket locker"],
  ["Ingredientes (nutrientes)", "Cooking ingredients"],
  ["Procesador de nutrientes", "Nutrient processor"],
  ["Plataforma de pesca", "Fishing platform"],
  ["Multiherramienta", "Multi-tool"],
  ["Carguero", "Freighter"],
  ["Exotraje", "Exosuit"],
  ["Carga (legado)", "Cargo (legacy)"],
  ["Tecnología", "Technology"],
  ["Inventario", "Inventory"],
];
function sectionLabel(label) {
  if (state.lang !== "en" || !label) return label || "";
  let out = label;
  SECTION_EN.forEach(([es, en]) => { out = out.split(es).join(en); });
  return out;
}

function renderInvList() {
  const invs = (state.snapshot && state.snapshot.inventories) || [];
  if (state.invIndex >= invs.length) state.invIndex = 0;
  let currentGroup = "";
  const html = [];
  invs.forEach((inv, index) => {
    const group = inv.group || "other";
    if (group !== currentGroup) {
      currentGroup = group;
      html.push(`<div class="inv-group">${escapeHtml(t("group_" + group))}</div>`);
    }
    const filled = inv.slots.length;
    const total = inv.capacity || Math.max(inv.width * inv.height, filled);
    // El punto marca la nave o la multiherramienta que llevas puestas ahora.
    const marked = inv.active && (group === "ship" || group === "multitool");
    html.push(`<button class="inv-item ${index === state.invIndex ? "active" : ""}" data-inv="${index}">
      <span>${marked ? `<i class="used-dot" title="${escapeAttr(t("active_label"))}"></i>` : ""}${
        escapeHtml(sectionLabel(inv.label))}</span>
      <span class="count">${filled}/${total || filled}</span>
    </button>`);
  });
  $("#inv-list").innerHTML = html.join("") || `<p class="muted">${t("empty_inv")}</p>`;

  $("#inv-list").querySelectorAll("[data-inv]").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.invIndex = Number(btn.dataset.inv);
      renderInvList();
      renderInvGrid();
    });
  });
}

function renderInvGrid() {
  const invs = (state.snapshot && state.snapshot.inventories) || [];
  const inv = invs[state.invIndex];
  const grid = $("#inv-grid");
  const empty = $("#inv-empty");
  if (!inv) {
    $("#inv-title").textContent = "–";
    $("#inv-count").textContent = "";
    grid.innerHTML = "";
    return;
  }
  $("#inv-title").textContent = sectionLabel(inv.label);
  const filled = inv.slots.length;
  const total = inv.capacity || Math.max(inv.width * inv.height, filled);
  $("#inv-count").textContent = `${filled}/${total || filled}` +
    (total > filled ? ` · ${total - filled} ${t("free_slots")}` : "");

  const filter = state.filter.trim().toLowerCase();
  // Con texto en el buscador se rastrean TODOS los contenedores: sirve para
  // ver de un vistazo en qué nave, caja o multiherramienta está el objeto.
  if (filter) {
    renderInvMatches(filter);
    return;
  }

  const type = state.typeFilter || "all";
  const items = inv.slots.filter((slot) => type === "all" || slot.type === type);
  grid.style.gridTemplateColumns = `repeat(${Math.max(inv.width, 1)}, minmax(0, 1fr))`;

  if (!items.length) {
    grid.innerHTML = "";
    empty.classList.remove("hidden");
    empty.textContent = type === "all" ? t("empty_inv") : t("no_match");
    return;
  }
  empty.classList.add("hidden");

  grid.innerHTML = items.map((slot) => {
    const info = db.info(slot.id);
    const names = info.names || {};
    const isTech = slot.type === "Technology";
    const isUnknown = !!slot.unknown || isUnknownId(slot.id);
    const amountText = isTech ? `${slot.amount}%` : fmtNumber(slot.amount);
    const color = info.color && /^[0-9A-Fa-f]{6}$/.test(info.color) ? "#" + info.color : "#4fd1e0";
    const title = nameOf(names) || (isUnknown ? t("unknown") : slot.id);
    const label = isUnknown ? "?" : (info.symbol || title.slice(0, 2));
    const icon = isUnknown
      ? `<span class="fallback" style="background:${CLASS_COLORS["?"]}">?</span>`
      : info.icon
        ? `<img onerror="this.outerHTML='<span class=\\'fallback\\' style=\\'background:${color}\\'>${jsq(label)}</span>'" src="${info.icon}" alt="">`
        : `<span class="fallback" style="background:${color}">${escapeHtml(label)}</span>`;
    const cls = info.class;
    const badge = isTech && cls
      ? `<span class="class-badge" style="background:${classColor(cls)}">${cls}</span>`
      : "";
    return `<div class="slot filled ${isTech ? "tech" : ""} ${slot.damage > 0.5 ? "damaged" : ""}"
      data-id="${escapeAttr(slot.id)}" data-amount="${slot.amount}" data-type="${slot.type}">
      ${info.symbol && !isUnknown ? `<span class="sym">${escapeHtml(info.symbol)}</span>` : ""}
      ${icon}
      ${badge}
      <span class="amount">${amountText}</span>
    </div>`;
  }).join("");
  bindSlots(grid);
}

function bindSlots(root) {
  root.querySelectorAll(".slot").forEach((el) => {
    el.addEventListener("mouseenter", (ev) => showTooltip(el, ev));
    el.addEventListener("mousemove", moveTooltip);
    el.addEventListener("mouseleave", hideTooltip);
    el.addEventListener("click", () => openItem(el.dataset.id));
  });
}

/* Búsqueda con texto: lista los coincidentes de todos los contenedores y
   indica dónde están. Al pulsar una fila se salta a ese contenedor. */
function renderInvMatches(filter) {
  const invs = (state.snapshot && state.snapshot.inventories) || [];
  const type = state.typeFilter || "all";
  const rows = [];
  for (let i = 0; i < invs.length && rows.length < 80; i += 1) {
    invs[i].slots.forEach((slot) => {
      if (rows.length >= 80) return;
      if (type !== "all" && slot.type !== type) return;
      const unknown = !!slot.unknown || isUnknownId(slot.id);
      const names = db.names(slot.id);
      const hit = unknown
        ? t("unknown").toLowerCase().includes(filter)
        : (slot.id + " " + nameOf(names) + " " + altOf(names))
            .toLowerCase().includes(filter);
      if (hit) rows.push({ inv: invs[i], index: i, slot, unknown });
    });
  }

  const grid = $("#inv-grid");
  const empty = $("#inv-empty");
  grid.style.gridTemplateColumns = "1fr";
  if (!rows.length) {
    grid.innerHTML = "";
    empty.classList.remove("hidden");
    empty.textContent = t("no_match");
    return;
  }
  empty.classList.add("hidden");
  grid.innerHTML = rows.map((row) => {
    const info = row.unknown
      ? { id: row.slot.id, names: {}, color: "9BA1A8", symbol: "?" }
      : db.info(row.slot.id);
    const names = info.names || {};
    const amount = row.slot.type === "Technology"
      ? `${row.slot.amount}%` : fmtNumber(row.slot.amount);
    return `<button class="glob-row" data-goto="${row.index}">
      ${thumb(info, "thumb")}
      <span class="g-name">${escapeHtml(
        row.unknown ? t("unknown") : nameOf(names) || row.slot.id)}</span>
      <span class="qty">×${amount}</span>
      <span class="g-where">${escapeHtml(sectionLabel(row.inv.label))}</span>
    </button>`;
  }).join("");

  grid.querySelectorAll("[data-goto]").forEach((el) => {
    el.addEventListener("click", () => {
      state.invIndex = Number(el.dataset.goto);
      state.filter = "";
      $("#inv-filter").value = "";
      renderInvList();
      renderInvGrid();
    });
  });
}

/* ---------------------------------------------------------------- partida */
function fmtPlayTime(seconds) {
  const s = Number(seconds || 0);
  if (!s) return "";
  return `${Math.floor(s / 3600)}h ${Math.floor((s % 3600) / 60)}m`;
}

function profileCard(label, value) {
  return `<div class="card"><small>${escapeHtml(label)}</small>${value}</div>`;
}

async function copyText(text) {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return true;
    }
  } catch (err) { /* se intenta de otra forma justo debajo */ }
  try {
    const box = document.createElement("textarea");
    box.value = text;
    box.style.position = "fixed";
    box.style.opacity = "0";
    document.body.appendChild(box);
    box.select();
    const ok = document.execCommand("copy");
    box.remove();
    return ok;
  } catch (err) {
    return false;
  }
}

function renderProfile() {
  const s = state.snapshot;
  if (!s) return;
  const save = s.save;
  const addr = save.address || {};
  const cards = [
    profileCard(t("state_label"), `<b>${escapeHtml(save.summary || "—")}</b>`),
    profileCard(t("mode_label"), `<b>${escapeHtml(save.mode || "—")}</b>`),
    profileCard(t("time_label"),
      `<b>${escapeHtml(fmtPlayTime(save.play_time) || "—")}</b>`),
    profileCard(t("galaxy_label"), `<b>${fmtNumber(save.galaxy || 0)}</b>`),
  ];
  if (addr.hex) {
    cards.push(profileCard(t("address_label"),
      `<span class="addr">
         <code id="addr-hex">${escapeHtml(addr.hex)}</code>
         <button class="ghost mini" id="addr-copy" title="${escapeAttr(t("copy"))}">⧉</button>
       </span>
       <small class="addr-sub">${escapeHtml(t("system_label"))} ${fmtNumber(addr.system)} ·
         ${escapeHtml(t("planet_label"))} ${fmtNumber(addr.planet)}</small>
       <div class="addr-actions">
         <button class="ghost mini" id="addr-glyphs">${escapeHtml(t("profile_glyphs"))}</button>
       </div>`));
  }
  $("#profile-cards").innerHTML = cards.join("");

  const glyphBtn = $("#addr-glyphs");
  if (glyphBtn) {
    glyphBtn.addEventListener("click", () => {
      switchView("tools");
      portalFromSave();
    });
  }

  const copyBtn = $("#addr-copy");
  if (copyBtn) {
    copyBtn.addEventListener("click", async () => {
      const ok = await copyText(addr.hex);
      copyBtn.textContent = ok ? "✓" : "?";
      copyBtn.title = ok ? t("copied") : t("copy");
      setTimeout(() => {
        copyBtn.textContent = "⧉";
        copyBtn.title = t("copy");
      }, 1600);
    });
  }

  renderFleet("#fleet-ships", s.ships || [], true);
  renderFleet("#fleet-tools", s.multitools || [], false);
  $("#fleet-ships-note").textContent =
    (s.ships || []).length ? `${fmtNumber((s.ships || []).length)}` : "";
}

function barRow(label, used, cap) {
  const total = cap || used;
  const pct = total ? Math.min(100, Math.round((used / total) * 100)) : 0;
  return `<div class="bar-row">
    <span>${escapeHtml(label)}</span>
    <span class="bar-num">${fmtNumber(used)}/${fmtNumber(total)}</span>
    <div class="bar"><i style="width:${pct}%"></i></div>
  </div>`;
}

function renderFleet(selector, list, isShip) {
  const box = $(selector);
  if (!box) return;
  if (!list.length) {
    box.innerHTML = `<p class="muted">${t("fleet_empty")}</p>`;
    return;
  }
  box.innerHTML = list.map((entry) => {
    const cls = entry.class || "";
    const bars = [];
    if (entry.capacity || entry.slots) {
      bars.push(barRow(isShip ? t("cargo_label") : t("slots_unit"),
        entry.slots, entry.capacity));
    }
    if (isShip && entry.tech_capacity) {
      bars.push(barRow(t("chip_tech"), entry.tech, entry.tech_capacity));
    }
    return `<div class="fleet-card">
      <div class="fleet-top">
        <span class="fallback fleet-mark" style="background:${classColor(cls)}">${
          escapeHtml(cls || "?")}</span>
        <div class="fleet-name">
          <h4>${escapeHtml(sectionLabel(entry.label))}</h4>
          <div class="badges">
            ${cls ? `<span class="badge class" style="--c:${classColor(cls)}">${
              escapeHtml(t("item_class"))} ${escapeHtml(cls)}</span>` : ""}
            ${entry.active ? `<span class="badge on">${
              escapeHtml(t("active_label"))}</span>` : ""}
          </div>
        </div>
      </div>
      ${bars.join("")}
      <button class="ghost mini" data-goto-key="${escapeAttr(entry.key)}">${
        escapeHtml(t("view_inv"))}</button>
    </div>`;
  }).join("");

  box.querySelectorAll("[data-goto-key]").forEach((btn) => {
    btn.addEventListener("click", () => gotoInventory(btn.dataset.gotoKey));
  });
}

function gotoInventory(key) {
  const invs = (state.snapshot && state.snapshot.inventories) || [];
  const index = invs.findIndex(
    (inv) => inv.key === key || inv.key.startsWith(`${key}:`));
  if (index < 0) return;
  state.invIndex = index;
  state.filter = "";
  $("#inv-filter").value = "";
  switchView("inventory");
  renderInvList();
  renderInvGrid();
}

/* ------------------------------------------------------- qué puedo hacer */
async function toggleCraftable() {
  const panel = $("#craftable-panel");
  if (!panel.classList.contains("hidden")) {
    panel.classList.add("hidden");
    return;
  }
  $("#goals-panel").classList.add("hidden");
  panel.classList.remove("hidden");
  await renderCraftable(state.craftKind);
}

async function renderCraftable(kind) {
  state.craftKind = kind || state.craftKind;
  const panel = $("#craftable-panel");
  panel.innerHTML = `<p class="muted">${t("please_wait")}</p>`;
  try {
    const data = await getJSON(`/api/craftable?kind=${state.craftKind}`);
    db.remember(data.results);
    const chips = `<div class="chips">
      <button class="chip-btn ${state.craftKind === "craft" ? "active" : ""}"
        data-kind="craft">${escapeHtml(t("tab_craft"))}</button>
      <button class="chip-btn ${state.craftKind === "refine" ? "active" : ""}"
        data-kind="refine">${escapeHtml(t("tab_refine"))}</button>
      <span class="chip-note">${fmtNumber(data.results.length)}</span>
    </div>`;
    const rows = data.results.slice(0, 60).map(craftRow).join("");
    const more = data.results.length > 60
      ? `<p class="muted more">… ${fmtNumber(data.results.length - 60)}</p>` : "";
    panel.innerHTML = chips +
      (rows || `<p class="muted">${t("craftable_none")}</p>`) + more;
    panel.querySelectorAll("[data-kind]").forEach((btn) => {
      btn.addEventListener("click", () => renderCraftable(btn.dataset.kind));
    });
    panel.querySelectorAll("[data-open]").forEach((el) => {
      el.addEventListener("click", () => openItem(el.dataset.open));
    });
  } catch (err) {
    panel.innerHTML = `<p class="muted">${escapeHtml(err.message)}</p>`;
  }
}

function craftRow(item) {
  const ingredients = item.need.map((ing) =>
    `${nameOf(ing.names) || ing.id} ×${fmtNumber(ing.amount)}`).join(" + ");
  const op = state.lang === "es" ? (item.op_es || item.op) : (item.op || item.op_es);
  const hint = [ingredients, op ? String(op) : ""].filter(Boolean).join(" · ");
  return `<button class="result" data-open="${escapeAttr(item.id)}">
    ${thumb(item, "thumb")}
    <span>
      <span class="r-name">${escapeHtml(nameOf(item.names) || item.id)}</span><br>
      <span class="r-alt">${escapeHtml(hint)}</span>
    </span>
    <span class="r-type"><i class="times">×${fmtNumber(item.times)}</i></span>
  </button>`;
}

/* --------------------------------------------------------------- objetivos */
function loadGoals() {
  try {
    return JSON.parse(localStorage.getItem("nms.goals")) || [];
  } catch (err) {
    return [];
  }
}

function saveGoals(list) {
  localStorage.setItem("nms.goals", JSON.stringify(list));
  updateGoalsCount();
}

function updateGoalsCount() {
  const counter = $("#goals-count");
  if (!counter) return;
  const n = loadGoals().length;
  counter.textContent = n ? `(${n})` : "";
}

const isGoal = (id) => loadGoals().some((goal) => goal.id === id);

function addGoal(id, qty) {
  const goals = loadGoals().filter((goal) => goal.id !== id);
  goals.push({ id, qty: Math.max(1, Number(qty) || 1) });
  saveGoals(goals);
}

function removeGoal(id) {
  saveGoals(loadGoals().filter((goal) => goal.id !== id));
}

async function toggleGoals() {
  const panel = $("#goals-panel");
  if (!panel.classList.contains("hidden")) {
    panel.classList.add("hidden");
    return;
  }
  $("#craftable-panel").classList.add("hidden");
  panel.classList.remove("hidden");
  await renderGoals();
}

async function renderGoals() {
  const panel = $("#goals-panel");
  const goals = loadGoals();
  if (!goals.length) {
    panel.innerHTML = `<p class="muted">${t("goals_empty")}</p>`;
    return;
  }
  panel.innerHTML = `<p class="muted">${t("please_wait")}</p>`;
  let plans;
  try {
    plans = await Promise.all(goals.map((goal) =>
      getJSON(`/api/plan/${encodeURIComponent(goal.id)}?n=${goal.qty}`)));
  } catch (err) {
    panel.innerHTML = `<p class="muted">${escapeHtml(err.message)}</p>`;
    return;
  }

  const shopping = {};
  plans.forEach((plan) => (plan.shopping || []).forEach((row) => {
    shopping[row.id] = (shopping[row.id] || 0) + row.need;
    db.remember([{ id: row.id, names: row.names }]);
  }));

  const rows = goals.map((goal, index) => {
    const root = plans[index].root;
    const info = db.info(root.id);
    if (root.names && Object.keys(root.names).length) {
      info.names = Object.assign({}, info.names, root.names);
      db.remember([info]);
    }
    const ok = !plans[index].shopping.length;
    return `<div class="goal-row">
      <button class="result" data-open="${escapeAttr(root.id)}">
        ${thumb(info, "thumb")}
        <span>
          <span class="r-name">${escapeHtml(nameOf(root.names) || root.id)}</span><br>
          <span class="r-alt">×${fmtNumber(goal.qty)}</span>
        </span>
        <span class="r-type">${ok
          ? `<i class="goal-ok" title="${escapeAttr(t("plan_ok"))}">✓</i>`
          : `<i class="times" title="${escapeAttr(t("shopping"))}"> ${
              fmtNumber(plans[index].shopping.length)}</i>`}</span>
      </button>
      <button class="ghost mini" data-drop="${escapeAttr(root.id)}"
        title="${escapeAttr(t("goal_remove"))}">×</button>
    </div>`;
  }).join("");

  const shopRows = Object.keys(shopping).map((id) => {
    const info = db.info(id);
    return `<div class="shop-row">
      ${thumb(info, "thumb")}
      <span>${escapeHtml(nameOf(info.names) || id)}</span>
      <span class="qty">×${fmtNumber(shopping[id])}</span>
    </div>`;
  }).join("");

  panel.innerHTML = `<div class="goal-list">${rows}</div>` +
    (shopRows
      ? `<h4 class="panel-sub">${escapeHtml(t("shopping"))}</h4>
         <div class="shop-list">${shopRows}</div>
         <button class="ghost mini" id="copy-shopping">${
           escapeHtml(t("copy_list"))}</button>`
      : `<p class="muted">${t("plan_ok")}</p>`);

  panel.querySelectorAll("[data-open]").forEach((el) => {
    el.addEventListener("click", () => openItem(el.dataset.open));
  });
  panel.querySelectorAll("[data-drop]").forEach((el) => {
    el.addEventListener("click", () => {
      removeGoal(el.dataset.drop);
      renderGoals();
    });
  });
  const copyBtn = $("#copy-shopping");
  if (copyBtn) {
    copyBtn.addEventListener("click", async () => {
      const text = Object.keys(shopping).map((id) => {
        const names = db.names(id);
        return `${nameOf(names) || id} × ${shopping[id]}`;
      }).join("\n");
      const ok = await copyText(text);
      copyBtn.textContent = ok ? t("copied") : t("copy_list");
      setTimeout(() => { copyBtn.textContent = t("copy_list"); }, 1600);
    });
  }
}

/* ------------------------------------------------------------------ plan */
async function loadPlan() {
  const box = $("#plan-box");
  const d = state.detail;
  if (!box || !d) return;
  const qty = state.planQty || 1;
  box.innerHTML = `<p class="muted">${t("please_wait")}</p>`;
  try {
    const plan = await getJSON(`/api/plan/${encodeURIComponent(d.id)}?n=${qty}`);
    const still = $("#plan-box");
    // Si mientras cargaba se abrió otra ficha, se descarta la respuesta.
    if (!still || !state.detail || state.detail.id !== d.id) return;
    if (plan.root.names && Object.keys(plan.root.names).length) {
      const info = db.info(plan.root.id);
      info.names = Object.assign({}, info.names, plan.root.names);
      db.remember([info]);
    }
    (plan.shopping || []).forEach((row) => db.remember([{ id: row.id, names: row.names }]));
    still.innerHTML = planNode(plan.root, true) + shoppingBlock(plan.shopping);
    still.querySelectorAll("[data-open]").forEach((el) => {
      el.addEventListener("click", () => openItem(el.dataset.open));
    });
  } catch (err) {
    const still = $("#plan-box");
    if (still) still.innerHTML = `<p class="muted">${escapeHtml(err.message)}</p>`;
  }
}

function planHead(node) {
  const info = node.id && db.items[node.id] ? db.items[node.id] : { id: node.id, names: node.names || {} };
  const label = nameOf(node.names) || nameOf(info.names) || node.id;
  let status;
  if (node.children && node.children.length) {
    const via = node.via === "refine" ? t("plan_by_refine") : t("plan_by_craft");
    status = `<span class="plan-via">${escapeHtml(via)} ×${fmtNumber(node.batches || 1)}</span>`;
  } else if (node.missing > 0) {
    status = `<span class="have miss">${t("missing")} ${fmtNumber(node.missing)}</span>`;
  } else {
    status = `<span class="have ok">${t("you_have")} ${fmtNumber(node.have)}</span>`;
  }
  return `${thumb(info)}
    <span class="plan-name" data-open="${escapeAttr(node.id)}"
      title="${escapeAttr(t("open_item"))}">${escapeHtml(label)}</span>
    <span class="qty">×${fmtNumber(node.need)}</span>${status}`;
}

function planNode(node, isRoot) {
  const head = planHead(node);
  if (!node.children || !node.children.length) {
    return `<div class="plan-node leaf ${node.missing > 0 ? "gap" : ""}">${head}</div>`;
  }
  return `<details class="plan-node" ${isRoot ? "open" : ""}>
    <summary>${head}</summary>
    <div class="plan-children">${node.children.map((c) => planNode(c, false)).join("")}</div>
  </details>`;
}

function shoppingBlock(shopping) {
  if (!shopping || !shopping.length) {
    return `<p class="plan-ok">✓ ${escapeHtml(t("plan_ok"))}</p>`;
  }
  return `<div class="shopping">
    <h4>${escapeHtml(t("shopping"))}</h4>
    ${shopping.map((row) => `<div class="shop-row">
      ${thumb(db.info(row.id), "thumb")}
      <span data-open="${escapeAttr(row.id)}">${escapeHtml(nameOf(row.names) || row.id)}</span>
      <span class="qty">×${fmtNumber(row.need)}</span>
    </div>`).join("")}
  </div>`;
}

/* -------------------------------------------------------------- tooltip */
function showTooltip(el, ev) {
  const id = el.dataset.id;
  const info = db.info(id);
  const names = info.names || {};
  const tip = $("#tooltip");
  if (isUnknownId(id)) {
    tip.innerHTML =
      `<b>${escapeHtml(t("unknown"))}</b>` +
      `<div class="t-desc">${escapeHtml(t("unknown_hint"))}</div>` +
      `<div class="t-hint">›</div>`;
    tip.classList.remove("hidden");
    moveTooltip(ev);
    return;
  }
  tip.innerHTML =
    `<b>${escapeHtml(nameOf(names) || id)}</b>` +
    (altOf(names) ? `<span class="t-alt">${escapeHtml(altOf(names))}</span>` : "") +
    (info.class
      ? `<span class="t-class" style="color:${classColor(info.class)}">` +
        `${escapeHtml(t("item_class"))} ${escapeHtml(info.class)}</span>` : "") +
    (info.descs && (info.descs[state.lang] || info.descs.en)
      ? `<div class="t-desc">${escapeHtml((info.descs[state.lang] || info.descs.en)).slice(0, 240)}…</div>` : "") +
    `<div class="t-hint">›</div>`;
  tip.classList.remove("hidden");
  moveTooltip(ev);
}
function moveTooltip(ev) {
  const tip = $("#tooltip");
  const pad = 14;
  let x = ev.clientX + pad;
  let y = ev.clientY + pad;
  const rect = tip.getBoundingClientRect();
  if (x + rect.width > window.innerWidth - 8) x = ev.clientX - rect.width - pad;
  if (y + rect.height > window.innerHeight - 8) y = ev.clientY - rect.height - pad;
  tip.style.left = `${x}px`;
  tip.style.top = `${y}px`;
}
function hideTooltip() { $("#tooltip").classList.add("hidden"); }

function escapeHtml(text) {
  return String(text).replace(/[&<>"]/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}
function escapeAttr(text) { return escapeHtml(text).replace(/'/g, "&#39;"); }

/* --------------------------------------------------------------- recetas */
const db = {
  items: {},
  info(id) {
    return this.items[id] || { id, names: {} };
  },
  names(id) { return this.info(id).names; },
  remember(list) {
    (list || []).forEach((item) => { this.items[item.id] = item; });
  },
};

async function runSearch() {
  const q = $("#search-input").value.trim();
  const box = $("#search-results");
  if (q.length < 2) { box.innerHTML = ""; return; }
  try {
    const data = await getJSON(`/api/search?q=${encodeURIComponent(q)}`);
    db.remember(data.results);
    if (!data.results.length) {
      box.innerHTML = `<p class="muted">${t("no_results")}</p>`;
      return;
    }
    box.innerHTML = data.results.map((item) => resultRow(item)).join("");
    box.querySelectorAll("[data-open]").forEach((el) => {
      el.addEventListener("click", () => openItem(el.dataset.open));
    });
  } catch (err) {
    box.innerHTML = `<p class="muted">${err.message}</p>`;
  }
}

function resultRow(item) {
  const hints = [];
  (item.obtain || []).forEach((kind) => hints.push(t(`obtain_${kind}`)));
  if (item.used_in) hints.push(t("obtain_used").replace("%s", item.used_in));
  return `<button class="result ${state.detail && state.detail.id === item.id ? "active" : ""}" data-open="${escapeAttr(item.id)}">
    ${thumb(item, "thumb")}
    <span>
      <span class="r-name">${escapeHtml(nameOf(item.names) || item.id)}</span><br>
      <span class="r-alt">${escapeHtml(altOf(item.names) || item.id)}</span>
      ${hints.length ? `<br><span class="r-hint">${escapeHtml(hints.join(" · "))}</span>` : ""}
    </span>
    <span class="r-type">${
      item.class ? `<i class="r-class" style="background:${classColor(item.class)}">${escapeHtml(item.class)}</i> ` : ""
    }${escapeHtml(item.type || "")}</span>
  </button>`;
}

async function openItem(id) {
  if (isUnknownId(id)) {
    renderMissingItem(id, true);
    return;
  }
  try {
    const detail = await getJSON(`/api/item/${encodeURIComponent(id)}`);
    state.detail = detail;
    state.missing = null;
    renderDetail(id);
    if (state.view !== "recipes") switchView("recipes");
    $("#recipe-detail").scrollIntoView({ block: "nearest" });
  } catch (err) {
    const message = String(err.message || "");
    if (message.startsWith("Objeto desconocido") || message.startsWith("Unknown")) {
      renderMissingItem(id, false);
      return;
    }
    $("#recipe-detail").innerHTML = `<p class="muted">${escapeHtml(message)}</p>`;
  }
}

/* Objeto que la base de datos no puede identificar: id ilegible del save o
   id válido que todavía no está catalogado. */
function renderMissingItem(id, unknown) {
  state.detail = null;
  state.missing = { id, unknown };
  $("#recipe-detail").innerHTML = `
    <div class="item-head">
      <span class="big-fallback" style="background:${CLASS_COLORS["?"]}">?</span>
      <div>
        <h2>${escapeHtml(unknown ? t("unknown") : id)}</h2>
        ${unknown ? "" : `<div class="badges"><span class="badge">${escapeHtml(id)}</span></div>`}
      </div>
    </div>
    <p class="desc">${escapeHtml(unknown ? t("unknown_hint") : t("no_data"))}</p>`;
  if (state.view !== "recipes") switchView("recipes");
  $("#recipe-detail").scrollIntoView({ block: "nearest" });
}

function totals() {
  return (state.snapshot && state.snapshot.totals) || {};
}

function haveBadge(needed, available) {
  const have = Math.min(available, needed);
  if (available >= needed) {
    return `<span class="have ok">${t("you_have")} ${fmtNumber(available)}</span>`;
  }
  return `<span class="have miss">${t("you_have")} ${fmtNumber(have)} · ` +
         `${t("missing")} ${fmtNumber(needed - available)}</span>`;
}

function ingredientLine(ing, available) {
  // El servidor ya manda los nombres de cada ingrediente; si llegan vacíos
  // (objeto fuera del catálogo) caemos a la caché local de la interfaz.
  const info = db.info(ing.id);
  if (ing.names && Object.keys(ing.names).length) {
    info.names = Object.assign({}, info.names, ing.names);
    db.remember([info]);
  }
  db.remember([info]);
  const names = info.names || {};
  const amount = Number(ing.amount || 1);
  return `<div class="line" data-open="${escapeAttr(ing.id)}" title="${t("open_item")}">
    ${thumb(info)}
    <span>${escapeHtml(nameOf(names) || ing.id)}</span>
    <span class="qty">×${fmtNumber(amount)}</span>
    ${haveBadge(amount, available)}
  </div>`;
}

function renderDetail(id) {
  const d = state.detail;
  if (!d) return;
  db.remember([d]);
  const totalsMap = totals();
  const html = [];

  html.push(`<div class="item-head">
    ${thumb(d, "big")}
    <div>
      <h2>${escapeHtml(nameOf(d.names) || d.id)}</h2>
      ${altOf(d.names) ? `<div class="alt">${escapeHtml(altOf(d.names))}</div>` : ""}
      <div class="badges">
        <span class="badge">${escapeHtml(d.id)}</span>
        ${d.class ? `<span class="badge class" style="--c:${classColor(d.class)}">` +
          `${escapeHtml(t("item_class"))} ${escapeHtml(d.class)}</span>` : ""}
        ${d.type ? `<span class="badge">${escapeHtml(d.type)}</span>` : ""}
        ${d.group ? `<span class="badge">${escapeHtml(d.group)}</span>` : ""}
        ${d.stack ? `<span class="badge">${t("stack")} ${fmtNumber(d.stack)}</span>` : ""}
        ${d.value ? `<span class="badge">${t("value")} ${fmtNumber(d.value)} ◈</span>` : ""}
        ${totalsMap[d.id] ? `<span class="badge">${t("you_have")} ${fmtNumber(totalsMap[d.id])}</span>` : ""}
      </div>
    </div>
  </div>`);

  const desc = d.descs && (d.descs[state.lang] || d.descs.en);
  if (desc) html.push(`<p class="desc">${escapeHtml(desc)}</p>`);
  if (!nameOf(d.names)) html.push(`<p class="desc">${escapeHtml(t("no_data"))}</p>`);

  if (d.craft) {
    const lines = d.craft.in.map((ing) =>
      ingredientLine(ing, totalsMap[ing.id] || 0)).join("");
    html.push(`<div class="recipe-block"><h3>${t("craft_title")}</h3>
      <div class="recipe">
        <div class="op">${escapeHtml(d.group || "")}</div>
        ${lines}
        <div class="line out-line">
          ${thumb(d)}
          <span>${escapeHtml(nameOf(d.names) || d.id)}</span>
          <span class="qty">×${fmtNumber(d.craft.out)}</span>
        </div>
      </div></div>`);
  }

  if (d.refine_out.length) {
    html.push(`<div class="recipe-block"><h3>${t("refine_out_title")}</h3>` +
      d.refine_out.map((r) => refineRecipe(r)).join("") + `</div>`);
  }

  // Si el objeto no tiene receta propia, se indica cómo conseguirlo.
  if (!d.craft && !d.refine_out.length) {
    const hints = [];
    if (d.type === "Substance") hints.push(t("obtain_gather"));
    if (d.used_in.length) hints.push(t("obtain_used").replace("%s", d.used_in.length));
    if (hints.length) html.push(`<p class="desc">${escapeHtml(hints.join(" · "))}</p>`);
  }

  if (d.refine_in.length) {
    html.push(`<div class="recipe-block"><h3>${t("refine_in_title")}</h3>` +
      d.refine_in.slice(0, 8).map((r) => refineRecipe(r)).join("") + `</div>`);
  }

  if (d.used_in.length) {
    html.push(`<div class="recipe-block"><h3>${t("used_in_title")}</h3>
      <div class="used-in">${d.used_in.map((item) => {
        db.remember([item]);
        return resultRow(item);
      }).join("")}</div></div>`);
  }

  // Plan: qué hace falta (y en qué orden) para conseguirlo, más el atajo de
  // marcarlo como objetivo para llevar la cuenta en la lista de objetivos.
  html.push(`<div class="recipe-block"><h3>${escapeHtml(t("plan_title"))}</h3>
    <div class="plan-tools">
      <label class="plan-qty">${escapeHtml(t("plan_qty"))}
        <input id="plan-qty" type="number" min="1" step="1" value="${state.planQty}">
      </label>
      <button id="goal-add" class="ghost mini ${isGoal(d.id) ? "on" : ""}">${
        isGoal(d.id) ? escapeHtml(t("in_goals")) : escapeHtml(t("goal_add"))}</button>
    </div>
    <div id="plan-box" class="plan-box"></div></div>`);

  $("#recipe-detail").innerHTML = html.join("");
  $("#recipe-detail").querySelectorAll("[data-open]").forEach((el) => {
    el.addEventListener("click", () => openItem(el.dataset.open));
  });

  const qtyInput = $("#plan-qty");
  if (qtyInput) {
    let timer = null;
    qtyInput.addEventListener("input", () => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        const value = Math.max(1, Number(qtyInput.value) || 1);
        state.planQty = value;
        loadPlan();
      }, 320);
    });
  }
  const goalBtn = $("#goal-add");
  if (goalBtn) {
    goalBtn.addEventListener("click", () => {
      if (isGoal(d.id)) removeGoal(d.id);
      else addGoal(d.id, state.planQty);
      const on = isGoal(d.id);
      goalBtn.classList.toggle("on", on);
      goalBtn.textContent = on ? t("in_goals") : t("goal_add");
      updateGoalsCount();
    });
  }
  loadPlan();
}

function refineRecipe(r) {
  const totalsMap = totals();
  const inputs = r.in.map((ing) => ingredientLine(ing, totalsMap[ing.id] || 0)).join("");
  const outInfo = db.info(r.out.id);
  if (r.out.names && Object.keys(r.out.names).length) {
    outInfo.names = Object.assign({}, outInfo.names, r.out.names);
  }
  db.remember([outInfo]);
  const time = r.time ? ` · ${Math.round(r.time)}${t("seconds")}` : "";
  const op = (state.lang === "es" && r.op_es) ? r.op_es : r.op;
  return `<div class="recipe">
    ${op ? `<div class="op">${escapeHtml(op)}${time}</div>` : ""}
    ${inputs}
    <div class="line out-line" data-open="${escapeAttr(r.out.id)}" title="${t("open_item")}">
      ${thumb(outInfo)}
      <span>${escapeHtml(nameOf(outInfo.names) || r.out.id)}</span>
      <span class="qty">×${fmtNumber(r.out.amount)}</span>
    </div>
  </div>`;
}

/* ------------------------------------------------- actualización de datos */
// Lanza tools/update_db.py en el servidor y va leyendo su log mientras corre.
const dbUpdate = { timer: null, count: 0, running: false, done: null, log: [] };

function openDbDialog() {
  $("#db-backdrop").classList.remove("hidden");
  renderDbState();
  if (dbUpdate.running) scheduleDbPoll(150);
}

function closeDbDialog() {
  $("#db-backdrop").classList.add("hidden");
}

function renderDbState() {
  const dot = $("#db-dot");
  const start = $("#db-start");
  const status = $("#db-status");
  const log = $("#db-log");
  if (dot) dot.classList.toggle("hidden", !dbUpdate.running);
  if (start) {
    start.disabled = dbUpdate.running;
    start.textContent = dbUpdate.running ? t("db_running_label") : t("db_start");
  }
  if (status) {
    if (dbUpdate.running) status.textContent = t("db_running");
    else if (dbUpdate.done === true) status.textContent = t("db_done");
    else if (dbUpdate.done === false) status.textContent = t("db_failed");
    else if (!dbUpdate.log.length) status.textContent = t("db_idle");
    else status.textContent = "";
  }
  if (log) {
    log.textContent = dbUpdate.log.join("\n");
    log.classList.toggle("hidden", !dbUpdate.log.length);
    log.scrollTop = log.scrollHeight;
  }
}

function scheduleDbPoll(delay) {
  clearTimeout(dbUpdate.timer);
  dbUpdate.timer = setTimeout(pollDbUpdate, delay);
}

async function pollDbUpdate() {
  try {
    const data = await getJSON(`/api/update/state?since=${dbUpdate.count}`);
    dbUpdate.count = data.count;
    if (data.lines && data.lines.length) {
      dbUpdate.log = dbUpdate.log.concat(data.lines).slice(-400);
    }
    if (dbUpdate.running && !data.running) {
      // Acaba de terminar: la BD nueva ya está en el servidor.
      dbUpdate.done = data.exit === 0;
      state.lastPayload = "";
      loadInventory();
    }
    dbUpdate.running = data.running;
    renderDbState();
    if (data.running) scheduleDbPoll(900);
  } catch (err) {
    dbUpdate.running = false;
    dbUpdate.done = false;
    renderDbState();
  }
}

async function startDbUpdate() {
  const what = $("#db-what").value;
  try {
    const res = await getJSON(`/api/update/start?what=${encodeURIComponent(what)}`);
    if (!res.started) {
      $("#db-status").textContent = t("db_busy");
      return;
    }
    dbUpdate.running = true;
    dbUpdate.done = null;
    dbUpdate.count = 0;
    dbUpdate.log = [];
    renderDbState();
    scheduleDbPoll(150);
  } catch (err) {
    $("#db-status").textContent = err.message || t("db_no_update");
  }
}

/* ----------------------------------------------------------- herramientas */
/* Líneas ley: calculadora de la comunidad (NMSCD/leylinecalc, MIT) con
   guardado de lecturas por planeta y navegador hasta la línea.
   Direcciones de portal: la misma fórmula que Coordinate-Conversion (MIT),
   que es la que usan el refuerzo de señal y los decoders. */
const ley = {
  data: { planet: "", planets: {}, values: {}, scale: 0, target: null },
  booted: false,
  lastMsg: null,
};

/* Mensajes del conversor: se guardan como clave para poder volver a
   traducirlos al cambiar de idioma. */
const portal = { addrMsg: null, out: null };

function loadLey() {
  try {
    const raw = JSON.parse(localStorage.getItem("nms.ley") || "{}");
    ley.data = Object.assign(
      { planet: "", planets: {}, values: {}, scale: 0, target: null }, raw);
  } catch (err) {
    localStorage.removeItem("nms.ley");
  }
}

function saveLey() {
  localStorage.setItem("nms.ley", JSON.stringify(ley.data));
}

function currentPlanetName() {
  const save = state.snapshot && state.snapshot.save;
  const summary = ((save && save.summary) || "").trim();
  const parts = /^([^(]+)\(([^)]{1,48})\)$/.exec(summary);
  return parts && /planet/i.test(parts[1]) ? parts[2].trim() : "";
}

function leyValues() {
  const num = (id) => {
    const value = parseFloat($(`#${id}`).value);
    return Number.isFinite(value) ? value : null;
  };
  return {
    lat1: num("ley-lat1"), long1: num("ley-long1"),
    lat2: num("ley-lat2"), long2: num("ley-long2"),
    dist: num("ley-dist"),
  };
}

function bootLey() {
  if (ley.booted) return;
  ley.booted = true;
  loadLey();
  const v = ley.data.values || {};
  const set = (id, value) => { $(`#${id}`).value = value === null || value === undefined ? "" : value; };
  set("ley-lat1", v.lat1); set("ley-long1", v.long1);
  set("ley-lat2", v.lat2); set("ley-long2", v.long2);
  set("ley-dist", v.dist);
  if (!ley.data.planet) ley.data.planet = currentPlanetName();
  $("#ley-planet").value = ley.data.planet || "";
  renderLeyPoints();
}

function leyLines(v) {
  const dLat = v.lat2 - v.lat1;
  const dLong = v.long2 - v.long1;
  const moved = Math.hypot(dLat, dLong);
  // Fórmula de la herramienta de la comunidad: separación entre líneas = 655 u.
  const spacing = (655 * moved) / v.dist;
  const lines = [];
  [-90, 0, 90, 180].forEach((angle) => {
    lines.push(angle + spacing / 2, angle - spacing / 2);
  });
  return {
    spacing,
    moved,
    values: lines.map((line) => {
      let fixed = line;
      while (fixed > 180) fixed -= 360;
      while (fixed < -180) fixed += 360;
      return Math.round(fixed * 100) / 100;
    }).sort((a, b) => b - a),
  };
}

function fmtDeg(value) {
  return `${value >= 0 ? "+" : ""}${value.toFixed(2)}°`;
}

function renderLeyLines(list) {
  $("#ley-lines").innerHTML = list.map((line) => `
    <button class="ley-line${line === ley.data.target ? " active" : ""}" data-long="${line}">
      ${fmtDeg(line)}
    </button>`).join("");
  $("#ley-lines").querySelectorAll(".ley-line").forEach((btn) => {
    btn.addEventListener("click", () => {
      ley.data.target = parseFloat(btn.dataset.long);
      saveLey();
      renderLeyLines(list);
      renderLeyNav();
    });
  });
}

function renderLeyNav() {
  const box = $("#ley-nav");
  const v = leyValues();
  const target = ley.data.target;
  const scale = ley.data.scale;
  if (target === null || target === undefined || !scale || v.long2 === null) {
    box.classList.add("hidden");
    return;
  }
  box.classList.remove("hidden");
  const delta = ((target - v.long2 + 540) % 360) - 180;
  const distance = Math.abs(delta) * scale;
  const here = distance < 2;
  const east = delta >= 0;
  box.innerHTML = `
    <div class="ley-nav-row">
      <span>${escapeHtml(t("ley_nav_target"))} <code>${fmtDeg(target)}</code></span>
      <span>${escapeHtml(t("ley_nav_pos"))} <code>${fmtDeg(v.long2)}</code></span>
      <span>${escapeHtml(t("ley_nav_dist"))} <b>${fmtNumber(Math.round(distance))} u</b></span>
      <span class="dir-badge ${here ? "" : (east ? "east" : "west")}">
        ${escapeHtml(here ? t("ley_nav_here")
          : `${east ? t("ley_dir_east") : t("ley_dir_west")} · ${east ? 90 : 270}°`)}
      </span>
    </div>
    <p class="muted">${escapeHtml(here ? t("ley_nav_hint") : t("ley_nav_walk"))}</p>`;
}

function leyMsgText() {
  if (ley.lastMsg === "ok") {
    return `${t("ley_lines_title")} · ${t("ley_valid")} · ` +
      `${t("ley_scale")} ${fmtNumber(Math.round(ley.data.scale))} u/°`;
  }
  return ley.lastMsg ? t(ley.lastMsg) : "";
}

function leyCalc() {
  const v = leyValues();
  const box = $("#ley-lines");
  const ok = v.lat1 !== null && v.long1 !== null && v.lat2 !== null &&
    v.long2 !== null && v.dist;
  const same = ok && Math.hypot(v.lat2 - v.lat1, v.long2 - v.long1) < 1e-9;
  if (!ok || same) {
    ley.lastMsg = ok ? "ley_same" : "ley_bad";
    $("#ley-msg").textContent = leyMsgText();
    box.classList.add("hidden");
    $("#ley-nav").classList.add("hidden");
    return;
  }
  const result = leyLines(v);
  ley.data.scale = v.dist / result.moved;
  // La línea objetivo solo se mantiene si sigue existiendo: al cambiar la
  // escala cambian las líneas, así que si no está, se coge la más cercana.
  if (ley.data.target === null || ley.data.target === undefined
      || !result.values.includes(ley.data.target)) {
    ley.data.target = result.values.reduce((best, line) =>
      Math.abs(line - v.long2) < Math.abs(best - v.long2) ? line : best,
      result.values[0]);
  }
  ley.data.values = v;
  ley.lastMsg = "ok";
  saveLey();
  $("#ley-msg").textContent = leyMsgText();
  renderLeyLines(result.values);
  renderLeyNav();
}

function renderLeyPoints() {
  const planet = ($("#ley-planet").value || "").trim();
  ley.data.planet = planet;
  saveLey();
  const list = (planet && ley.data.planets[planet]) || [];
  const ul = $("#ley-points-list");
  if (!list.length) {
    ul.innerHTML = `<li class="muted">${escapeHtml(t("ley_point_empty"))}</li>`;
    return;
  }
  ul.innerHTML = list.map((point, index) => `
    <li>
      <b>${escapeHtml(point.name)}</b>
      <code>${fmtDeg(point.lat).replace("°", "")} · ${fmtDeg(point.long)}</code>
      <button class="ghost mini" data-use="1" data-i="${index}"
              title="${escapeAttr(t("ley_fill1"))}">1</button>
      <button class="ghost mini" data-use="2" data-i="${index}"
              title="${escapeAttr(t("ley_fill2"))}">2</button>
      <button class="ghost mini" data-del="${index}"
              title="${escapeAttr(t("ley_point_del"))}">✕</button>
    </li>`).join("");
  ul.querySelectorAll("[data-use]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const point = list[Number(btn.dataset.i)];
      const which = btn.dataset.use;
      $(`#ley-lat${which}`).value = point.lat;
      $(`#ley-long${which}`).value = point.long;
      ley.data.values = leyValues();
      saveLey();
      renderLeyNav();
    });
  });
  ul.querySelectorAll("[data-del]").forEach((btn) => {
    btn.addEventListener("click", () => {
      list.splice(Number(btn.dataset.del), 1);
      if (!list.length) delete ley.data.planets[planet];
      saveLey();
      renderLeyPoints();
    });
  });
}

function addLeyPoint() {
  const planet = ($("#ley-planet").value || "").trim();
  const name = $("#ley-point-name").value.trim();
  const lat = parseFloat($("#ley-point-lat").value);
  const long = parseFloat($("#ley-point-long").value);
  if (!planet || !Number.isFinite(lat) || !Number.isFinite(long)) {
    ley.lastMsg = "ley_point_bad";
    $("#ley-msg").textContent = leyMsgText();
    return;
  }
  const list = ley.data.planets[planet] || (ley.data.planets[planet] = []);
  list.push({ name: name || t("ley_point_new"), lat, long });
  $("#ley-point-name").value = "";
  $("#ley-point-lat").value = "";
  $("#ley-point-long").value = "";
  saveLey();
  renderLeyPoints();
}

/* Conversión de direcciones: glifos = (coordenada + 2049) mod 4096 en X/Z y
   (coordenada + 129) mod 256 en Y; la inversa suma 2047 y 127. */
function mod(value, size) {
  return ((value % size) + size) % size;
}

function addrToGlyphs(addr) {
  const hex2 = (n) => mod(n, 256).toString(16).toUpperCase().padStart(2, "0");
  const hex3 = (n) => mod(n, 4096).toString(16).toUpperCase().padStart(3, "0");
  const code = `${mod(addr.planet, 16).toString(16).toUpperCase()}` +
    `${hex3(addr.system)}${hex2(addr.y + 129)}${hex3(addr.z + 2049)}` +
    `${hex3(addr.x + 2049)}`;
  return code.length === 12 ? code : "";
}

function glyphsToAddr(code) {
  const clean = String(code).trim().toUpperCase().replace(/[^0-9A-F]/g, "");
  if (clean.length !== 12) return null;
  return {
    planet: parseInt(clean[0], 16),
    system: parseInt(clean.slice(1, 4), 16),
    y: mod(parseInt(clean.slice(4, 6), 16) + 127, 256),
    z: mod(parseInt(clean.slice(6, 9), 16) + 2047, 4096),
    x: mod(parseInt(clean.slice(9, 12), 16) + 2047, 4096),
  };
}

function parseAddr(text) {
  const clean = String(text).trim().toUpperCase().replace(/\s+/g, "");
  let parts;
  if (clean.includes(":")) parts = clean.split(":");
  else if (clean.length === 16) {
    parts = [clean.slice(0, 4), clean.slice(4, 8), clean.slice(8, 12), clean.slice(12, 16)];
  } else return null;
  if (parts.length !== 4 || parts.some((p) => !/^[0-9A-F]{1,4}$/.test(p))) return null;
  const [x, y, z, system] = parts.map((p) => parseInt(p, 16));
  if (x > 4095 || y > 255 || z > 4095 || system > 4095) return null;
  return { x, y, z, system, planet: parseInt(($("#portal-planet").value || "0"), 10) };
}

function fmtAddr(addr) {
  const p4 = (n) => mod(n, 65536).toString(16).toUpperCase().padStart(4, "0");
  return `${p4(addr.x)}:${p4(addr.y)}:${p4(addr.z)}:${p4(addr.system)}`;
}

function glyphTiles(code) {
  const groups = [
    [code[0]], [code[1], code[2], code[3]], [code[4], code[5]],
    [code[6], code[7], code[8]], [code[9], code[10], code[11]],
  ];
  return groups.map((group) => `<span class="glyph-part">${
    group.map((ch) => `<span class="glyph">` +
      `<img src="/glyphs/${ch.toLowerCase()}.png" alt="${ch}"` +
      ` onerror="this.parentNode.classList.add('noimg')">` +
      `<b>${ch}</b></span>`).join("")
  }</span>`).join("");
}

function renderPortalTexts() {
  $("#portal-msg").textContent = portal.addrMsg ? t(portal.addrMsg) : "";
  const out = $("#portal-out");
  const data = portal.out;
  if (!data) {
    out.innerHTML = "";
    return;
  }
  if (data.err) {
    out.textContent = t(data.err);
    return;
  }
  const text = fmtAddr(data.addr);
  out.innerHTML = `<span class="addr"><code>${escapeHtml(text)}</code>
    <button class="ghost mini" id="portal-out-copy" title="${escapeAttr(t("copy"))}">⧉</button></span>
    <small class="addr-sub">${escapeHtml(t("planet_label"))} ${fmtNumber(data.addr.planet)} ·
    ${escapeHtml(t("system_label"))} ${fmtNumber(data.addr.system)}</small>`;
  $("#portal-out-copy").addEventListener("click", async (ev) => {
    ev.currentTarget.textContent = (await copyText(text)) ? "✓" : "?";
    setTimeout(() => { ev.currentTarget.textContent = "⧉"; }, 1500);
  });
}

function showGlyphs() {
  const addr = parseAddr($("#portal-addr").value);
  const code = addr && addrToGlyphs(addr);
  if (!code) {
    portal.addrMsg = "portal_bad_addr";
    $("#portal-glyphs").classList.add("hidden");
    $("#portal-code-row").classList.add("hidden");
    $("#portal-msg").textContent = t(portal.addrMsg);
    return;
  }
  portal.addrMsg = null;
  $("#portal-msg").textContent = "";
  $("#portal-glyphs").classList.remove("hidden");
  $("#portal-glyphs").innerHTML =
    glyphTiles(code) + `<div class="glyph-note">${escapeHtml(t("portal_breakdown"))}</div>`;
  $("#portal-code-row").classList.remove("hidden");
  $("#portal-code").textContent = code;
}

function showAddrFromGlyphs() {
  const addr = glyphsToAddr($("#portal-glyphs-in").value);
  portal.out = addr ? { addr } : { err: "portal_bad_glyphs" };
  if (addr) $("#portal-planet").value = String(addr.planet);
  renderPortalTexts();
}

function portalFromSave() {
  const save = state.snapshot && state.snapshot.save;
  const addr = (save && save.address) || {};
  if (!addr.hex) return false;
  $("#portal-addr").value = addr.hex;
  $("#portal-planet").value = String(addr.planet || 0);
  showGlyphs();
  return true;
}

function renderTools() {
  bootLey();
  const planetInput = $("#ley-planet");
  if (document.activeElement !== planetInput) {
    planetInput.value = ley.data.planet || "";
  }
  const planet = $("#portal-planet");
  if (!planet.options.length) {
    planet.innerHTML = [0, 1, 2, 3, 4, 5]
      .map((n) => `<option value="${n}">${n}</option>`).join("");
    planet.title = t("portal_planet_title");
  } else {
    planet.title = t("portal_planet_title");
  }
  if ($("#portal-glyphs").innerHTML) showGlyphs();
  renderPortalTexts();
  $("#ley-msg").textContent = leyMsgText();
  renderLeyPoints();
  renderLeyNav();
}

/* ------------------------------------------------------------- navegación */
function switchView(view) {
  state.view = view;
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.view === view);
  });
  $("#view-inventory").classList.toggle("hidden", view !== "inventory");
  $("#view-recipes").classList.toggle("hidden", view !== "recipes");
  $("#view-profile").classList.toggle("hidden", view !== "profile");
  $("#view-tools").classList.toggle("hidden", view !== "tools");
  if (view === "profile") renderProfile();
  if (view === "tools") renderTools();
  if (view === "recipes" && !$("#search-results").innerHTML) {
    $("#search-input").focus();
  }
}

/* ----------------------------------------------------------------- arranque */
function bindEvents() {
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.addEventListener("click", () => switchView(tab.dataset.view));
  });
  $("#lang-toggle").addEventListener("click", () => {
    state.lang = state.lang === "es" ? "en" : "es";
    localStorage.setItem("nms.lang", state.lang);
    applyI18n();
    renderHeader();
    renderVitals();
    renderInvList();
    renderInvGrid();
    renderProfile();
    updateGoalsCount();
    renderDbState();
    if (state.view === "tools") renderTools();
    if (!$("#craftable-panel").classList.contains("hidden")) {
      renderCraftable(state.craftKind);
    }
    if (!$("#goals-panel").classList.contains("hidden")) renderGoals();
    if (state.status) renderSaveSelect();
    if (state.detail) renderDetail(state.detail.id);
    else if (state.missing) renderMissingItem(state.missing.id, state.missing.unknown);
    if ($("#search-input").value.trim().length >= 2) runSearch();
  });
  $("#inv-filter").addEventListener("input", (ev) => {
    state.filter = ev.target.value;
    renderInvGrid();
  });
  // Filtro por tipo de objeto dentro del contenedor actual.
  $("#inv-chips").querySelectorAll("[data-type]").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.typeFilter = btn.dataset.type;
      $("#inv-chips").querySelectorAll("[data-type]").forEach((other) => {
        other.classList.toggle("active", other === btn);
      });
      renderInvGrid();
    });
  });
  $("#craftable-btn").addEventListener("click", toggleCraftable);
  $("#goals-btn").addEventListener("click", toggleGoals);
  $("#db-btn").addEventListener("click", openDbDialog);
  $("#db-close").addEventListener("click", closeDbDialog);
  $("#db-start").addEventListener("click", startDbUpdate);
  $("#db-backdrop").addEventListener("click", (ev) => {
    if (ev.target === $("#db-backdrop")) closeDbDialog();
  });
  // Herramientas: líneas ley y direcciones de portal.
  ["ley-lat1", "ley-long1", "ley-lat2", "ley-long2", "ley-dist"].forEach((id) => {
    $(`#${id}`).addEventListener("input", () => {
      ley.data.values = leyValues();
      saveLey();
      renderLeyNav();
    });
  });
  $("#ley-calc").addEventListener("click", leyCalc);
  $("#ley-point-add").addEventListener("click", addLeyPoint);
  $("#ley-planet").addEventListener("input", renderLeyPoints);
  $("#portal-to-glyphs").addEventListener("click", showGlyphs);
  $("#portal-to-addr").addEventListener("click", showAddrFromGlyphs);
  $("#portal-use-save").addEventListener("click", portalFromSave);
  $("#portal-code-copy").addEventListener("click", async (ev) => {
    const ok = await copyText($("#portal-code").textContent);
    ev.currentTarget.textContent = ok ? "✓" : "?";
    setTimeout(() => { ev.currentTarget.textContent = "⧉"; }, 1500);
  });
  [["portal-addr", showGlyphs], ["portal-glyphs-in", showAddrFromGlyphs]]
    .forEach(([id, handler]) => {
      $(`#${id}`).addEventListener("keydown", (ev) => {
        if (ev.key === "Enter") handler();
      });
    });
  let searchTimer = null;
  $("#search-input").addEventListener("input", () => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(runSearch, 180);
  });
  $("#save-select").addEventListener("change", async (ev) => {
    await getJSON(`/api/select?i=${ev.target.value}`);
    state.lastPayload = "";
    await loadInventory();
  });
}

async function start() {
  applyI18n();
  bindEvents();
  $("#save-meta").textContent = t("loading");
  await loadStatus();
  await loadInventory();
  setInterval(loadInventory, 2500);
  setInterval(loadStatus, 30000);
}

document.addEventListener("DOMContentLoaded", start);
