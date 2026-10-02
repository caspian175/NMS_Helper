/* Ejecuta la API estática de la web con node y la compara con los
 * resultados que ha calculado Python (tools/static_parity.py).
 *
 *   node tools/static_parity.js casos.json data/db.json
 *
 * Los objetos se comparan con las claves ordenadas y los números
 * normalizados, para que solo cuente el contenido y no el orden en que
 * cada lenguaje construye sus diccionarios.
 */
"use strict";

const fs = require("fs");
const { createApi } = require("../web/static-db.js");

function canon(valor) {
  if (Array.isArray(valor)) return valor.map(canon);
  if (valor && typeof valor === "object") {
    const salida = {};
    for (const clave of Object.keys(valor).sort()) salida[clave] = canon(valor[clave]);
    return salida;
  }
  if (typeof valor === "number" && Number.isFinite(valor)) {
    return Math.round(valor * 1e9) / 1e9;   // 320.0 de Python == 320 de JS
  }
  return valor;
}

async function main() {
  const [casosPath, dbPath] = process.argv.slice(2);
  if (!casosPath || !dbPath) {
    console.error("uso: node tools/static_parity.js casos.json db.json");
    process.exit(2);
  }
  const casos = JSON.parse(fs.readFileSync(casosPath, "utf8"));
  const esperado = casos.esperado;
  const api = createApi(JSON.parse(fs.readFileSync(dbPath, "utf8")));

  let total = 0;
  let fallos = 0;
  function cmp(etiqueta, obtenido, desea) {
    total += 1;
    const a = JSON.stringify(canon(obtenido));
    const b = JSON.stringify(canon(desea));
    if (a === b) {
      console.log(`  OK    ${etiqueta}`);
      return;
    }
    fallos += 1;
    console.log(`  FALLO ${etiqueta}`);
    console.log(`    js : ${a.slice(0, 700)}`);
    console.log(`    py : ${b.slice(0, 700)}`);
  }

  for (const consulta of casos.search) {
    cmp(`search ${JSON.stringify(consulta)}`,
      api.search(consulta), esperado.search[consulta]);
  }
  for (const id of casos.detail) {
    cmp(`detail ${id}`, api.detail(id), esperado.detail[id]);
  }
  for (const kind of casos.craftable) {
    cmp(`craftable ${kind}`, api.craftable({}, kind), esperado.craftable[kind]);
  }
  for (const [id, qty] of casos.plan) {
    cmp(`plan ${id} x${qty}`, api.plan(id, qty, {}), esperado.plan[`${id}|${qty}`]);
  }
  cmp("status", api.status(), esperado.estado);

  // Enrutado: misma respuesta (o mismo error) que server.handle_api().
  for (const url of casos.rutas) {
    const desea = esperado.rutas[url];
    try {
      const obtenido = await api.handle(url);
      if (desea.error !== undefined) {
        total += 1;
        fallos += 1;
        console.log(`  FALLO handle ${url}: esperaba error «${desea.error}»`);
        continue;
      }
      cmp(`handle ${url}`, obtenido, desea.result);
    } catch (err) {
      total += 1;
      if (desea.error !== undefined && String(err.message) === desea.error) {
        console.log(`  OK    handle ${url} (error esperado)`);
      } else {
        fallos += 1;
        console.log(`  FALLO handle ${url}: error «${err.message}», ` +
          `esperaba ${desea.error !== undefined ? `«${desea.error}»` : "respuesta"}`);
      }
    }
  }

  console.log(`${total - fallos}/${total} comprobaciones correctas.`);
  process.exit(fallos ? 1 : 0);
}

main().catch((err) => {
  console.error(err);
  process.exit(2);
});
