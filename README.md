# NMS Helper

Helper local para **No Man's Sky**: muestra tu inventario en tiempo real (con
toda tu flota), te dice **qué puedes fabricar ya**, te traza el plan para
conseguir lo que te falta y te ayuda con recetas de fabricación y refinado.
Además trae una **calculadora de líneas ley** y un **conversor de direcciones
de portal**.

100 % local: no sale nada de tu ordenador y **no necesita instalar nada más
que Python** (la única dependencia opcional es `pywebview`, para abrirlo en
ventana; sin ella se abre en el navegador y funciona igual).

```
python run.py
```

Se abre en una ventana de aplicación (o en el navegador si no hay `pywebview`).
Puedes dejarlo en una segunda ventana o en una pantalla secundaria mientras
juegas: cada 2,5 s vuelve a leer tu partida y actualiza la interfaz sola.

**¿Prefieres no instalar Python?** Hay un ejecutable para Windows en las
[releases](#instalar-el-ejecutable-de-windows) — 13 MB, sin instalación. Y si
te da cosa descargar un `.exe`, siempre puedes usar `python run.py`.

### La primera vez

Con el `.exe` **no hay que preparar nada**: la base de datos (objetos,
recetas y textos en español) y los glifos de portal ya vienen dentro, así que
al abrirlo tienes el inventario, las recetas y las herramientas en marcha.

Lo único que no viene son los **iconos del catálogo** (219 MB, que no tiene
sentido meter en un ejecutable de 13 MB). Hasta que los bajes, los iconos se
piden a las fuentes comunitarias y hacen falta algo de conexión; a partir de
ahí la herramienta va **100 % local**. Se bajan con un botón:

**Actualizar datos → Solo iconos (todo el catálogo)**

Mismo botón para lo demás, que es lo que hay que pulsar **tras un parche de
No Man's Sky**: *Actualizar datos → Todo*.

---

## Qué hace

**Inventario en vivo**
- Lee tus archivos de guardado (`%APPDATA%\HelloGames\NMS\st_*\save*.hg`).
- Muestra **toda la flota**: exotraje (inventario / tecnología), las naves
  de `ShipOwnership` (carga y tecnología de cada una), las
  multiherramientas guardadas, el carguero y los contenedores del refugio.
  Las secciones de «carga» solo aparecen si tu partida guarda algo ahí (el
  juego actual solo usa dos pestañas por contenedor).
- Las secciones van **agrupadas** (Exotraje · Flota · Multiherramientas ·
  Carguero · Refugio y cajas) y la nave o la multiherramienta que llevas
  puestas llevan un punto verde.
- **Huecos reales**: el total de cada contenedor es `ValidSlotIndices`
  (el exotraje tiene 46 huecos, no las 120 celdas de la cuadrícula), con
  los huecos libres a la vista.
- **Filtro por tipo** (todo / sustancias / productos / tecnología) y
  **búsqueda en todos los contenedores a la vez**: al escribir en el buscador
  se lista cada coincidencia con el sitio exacto donde está («Nave 2 ·
  Inventario») y un clic salta a esa sección.
- Monedas: unidades, nanitas y quicksilver.
- Estado: salud, escudo, energía, salud/escudo de la nave y munición.
- Selector de partida **agrupado por partida**: el juego escribe dos archivos
  por partida (un autosave y un punto de restauración: `save.hg` +
  `save2.hg`), aquí aparecen juntos como «Partida 1» y se indica cuál es el
  más reciente (el que se escribió de último).
- En las secciones de tecnología, cada módulo lleva su **clase**
  (C/B/A/S/X/?) con el color que usa el propio juego.
- Tooltip con descripción.
- Las ranuras con un id ilegible en el guardado se muestran como
  «objeto desconocido» y se pueden pulsar para ver qué pasa.

**Buscador de recetas**
- Busca por nombre en español o en inglés (y por ID del juego).
- Ficha del objeto con descripción, tipo, pila y valor.
- Receta de fabricación (fabricador) con sus ingredientes.
- Recetas de refinado: las que producen el objeto y las que lo consumen,
  con la **operación traducida** («alquimia cromática», no `Extract
  Chromatic Material`).
- **Cuánto te falta**: cruza los ingredientes con lo que llevas en el
  inventario y marca ✅ tienes / ⚠️ te faltan X.
- "Se usa para fabricar": qué otros objetos necesitan ese ingrediente.
- En los resultados de búsqueda se indica **cómo obtener** el objeto
  (se fabrica / se refina / se recolecta) y en cuántas recetas entra.
- Los ingredientes y el resultado de cada receta son **clicables**: abren
  la ficha del objeto.

**¿Qué puedo hacer ahora?** (botón en Recetas)
- Cruza lo que llevas encima con las 458 recetas de fabricación y las 357
  de refinado y lista **todo lo que puedes hacer ya mismo**, con las veces
  que sale (`×12`) y sus ingredientes. Dos pestañas: Fabricación / Refinado.

**Plan de crafteo y objetivos**
- En la ficha de cualquier objeto: **plan para conseguirlo**, con una
  cantidad editable. Expande la receta (y si hace falta, la de refinado)
  hasta los materiales base, indicando en cada nivel «se fabrica ×3» /
  «se refina ×1» y, en las hojas, lo que tienes y lo que falta. El árbol es
  plegable y cada nombre salta a su ficha.
- Si falta material se muestra la **lista de la compra**.
- Botón **«Añadir a objetivos»**: los objetivos se guardan en el navegador
  (localStorage) y el botón «Objetivos» de la izquierda muestra en qué estado
  está cada uno ✓ / ⚠️, la compra agregada de todos ellos y un botón para
  **copiar la lista** al portapapeles.

**Pestaña Partida**
- Ficha: ubicación (`SaveSummary`), modo, tiempo jugado, galaxia y
  **dirección galáctica** en el formato que comparte la comunidad
  (`046A:0081:0D6D:0038`, el mismo que enseña el refuerzo de señal), con
  botón de copiar y el sistema y el planeta actuales, más un atajo a «Ver
  glifos» que abre el conversor de portales con esa dirección puesta.
- Ojo con el dato que trae el guardado: allí las coordenadas se llaman
  `VoxelX/VoxelY/VoxelZ` y van **con signo y centradas en 0** (X y Z entre
  −2048 y 2047, Y entre −128 y 127). El refuerzo de señal enseña ese mismo
  número **desplazado** (+2047 en X/Z y +127 en Y), y por eso aquí se
  convierte al formato de la comunidad antes de mostrarlo; las coordenadas
  «voxel» crudas también viajan en la respuesta de la API (`address.voxel`).
- **Flota**: tarjeta por nave y por multiherramienta con su clase
  (C/B/A/S), si está en uso y sus barras de huecos; «Ver inventario» salta
  a esa sección del inventario.

**Pestaña Herramientas**

*Líneas ley*
- Reproduce la calculadora de la comunidad
  ([NMSCD/leylinecalc](https://github.com/NMSCD/leylinecalc), MIT): dos
  lecturas de lat/long más la distancia recorrida (mínimo 1000 u) y los
  ocho **meridianos candidatos** donde salen los tres depósitos. La escala
  que sale de ahí (unidades por grado) se muestra junto al resultado.
- **Navegador**: eliges una de las líneas y te dice cuánto te falta hasta
  ella, en qué dirección (Este/Oeste con su rumbo) y que después tires al
  norte o al sur, que es por donde están los depósitos.
- **Puntos guardados por planeta**: cada planeta (por defecto, el que estás
  pisando según el `SaveSummary`) guarda las lecturas que tomaste, con
  botones para usarlas como lectura 1 o 2 sin volver a teclearlas. Se guarda
  en el navegador, como los objetivos.

*Dirección de portal*
- Dirección galáctica → **12 glifos** (`1` + `0E4` + `05` + `666` + `2A0`),
  con el dibujo de cada glifo (los 16 símbolos de la rueda del portal, con su
  cifra en hexadecimal en la esquina), el código listo para copiar y el
  reparto `planeta · sistema · Y · Z · X`. El botón «Usar mi dirección» pone
  la de la partida actual.
- Y a la inversa: pegas un código de 12 glifos y sale la dirección
  `046A:0081:0D6D:0038` con su planeta y su sistema.
- La conversión es la misma que usan el decodificador de portales y
  [NMSCD/Coordinate-Conversion](https://github.com/NMSCD/Coordinate-Conversion)
  (MIT): glifo = (coordenada + 2049) mod 4096 en X/Z y (coordenada + 129)
  mod 256 en Y; el índice de sistema va tal cual y delante va un glifo con
  el índice de planeta. Se puede comprobar con el ejemplo de la wiki:
  `06B2:007F:01A9:0210` da `?210009AAEB3` (el `?` es el planeta). Con la
  partida de aquí, `0A9F:0084:0E65:00E4` da `10E4056662A0`.

**Actualizar datos** (botón en la barra de pestañas)
- Lanza `tools/update_db.py` desde la propia interfaz y va mostrando su log
  en directo: sirve para **tras un parche del juego** volver a bajar las
  tablas de la comunidad y los textos sin abrir una consola.
- Cuatro alcances: *todo*, *solo tablas* (recetas y objetos), *solo textos* o
  *solo iconos*. Mientras corre se desactiva el botón y se enciende un punto
  naranja en la barra; al terminar se recarga `db.json` (y `jsonmap.txt`, si
  cambió) sin reiniciar nada. En segundo plano se ejecuta con `--lang`,
  `--tables`, `--icons` o sin argumentos, igual que si lo lanzaras a mano.
- Con *solo iconos* entra `tools/fetch_icons.py`, que baja lo que falte del
  catálogo a `data/icons/` (wiki primero y luego el proveedor de `db.json`).
  Como ya está descargado, repetirlo solo baja los que falten.

**Idioma**: botón `EN`/`ES` en la cabecera para alternar entre el nombre en
español (como lo ves en partida) y el inglés (más cómodo para wikis).

---

## Cómo funciona

| Pieza | Detalle |
| --- | --- |
| Formato de partida | JSON comprimido en bloques LZ4 (magia `0xFEEDA1E5`), con las claves ofuscadas a 3 caracteres. Implementado en `nms_helper/save.py` con la stdlib de Python. |
| Mapa de claves | `data/jsonmap.txt` (comunidad, nmstoolkit). |
| Datos de objetos y recetas | `data/db.json`, generado por `tools/build_db.py` a partir de tres fuentes comunitarias. |
| Servidor | `http.server` de la stdlib, solo escucha en `127.0.0.1`. |
| Interfaz | HTML/CSS/JS puro en `web/`. |

El save solo se vuelve a parsear si cambia su fecha de modificación, así que
el coste por refresco es nulo mientras no guardes. Lo mismo con la base de
datos: si `data/db.json` cambia, el servidor la recarga sola, sin reiniciar.

### Fuentes de datos (base comunitaria)

- [pljeroen/nmstoolkit](https://github.com/pljeroen/nmstoolkit) → IDs de
  objeto (los mismos que usa el save) y mapa de claves.
- [ApexFatality93/NMS-Handbook](https://github.com/ApexFatality93/NMS-Handbook)
  → tablas de recetas (`Crafting_Table`, `Refining_Table`, sustancias,
  productos y tecnología) extraídas de los archivos del juego, **diez tablas
  complementarias** (piezas de edificio, legado, corbeta, nave, carnadas,
  fósiles, peces…) que rellenan huecos de icono y nombre, y **iconos**
  (los PNG descomprimidos de los DDS del juego). Para los iconos son la
  segunda fuente, detrás de la wiki.
- [Assistant for No Man's Sky](https://www.nmsassistant.com/) → nombres y
  descripciones en español. Sus 24 iconos son el último respaldo: solo entran
  los objetos a los que no llega ni la wiki ni el Handbook.
- [No Man's Sky Portals Decoder](https://nmsportals.github.io/) → los **16
  glifos de portal** (`data/glyphs/`), los mismos símbolos de la rueda del
  portal que se ven dentro del juego. Se bajan una sola vez con
  `python tools/fetch_glyphs.py` y el servidor los sirve en `/glyphs/…` (como
  los iconos, para que el conversor funcione sin conexión). Si algún día
  faltara alguno, la casilla muestra su cifra hexadecimal en su lugar.
- [Wiki de No Man's Sky](https://nomanssky.fandom.com/) → **los iconos,
  con prioridad sobre el resto**. Para cada objeto se intenta la imagen de su
  ficha (`|image =`) y, si no hay ficha, el nombre del fichero deducido del
  icono que ya traía el Handbook (`substance.fuel.1.png` →
  `File:SUBSTANCE.FUEL.1.png`). La wiki cubre 1 867 de los 3 930 nombres en
  inglés que hay en `db.json` (47 %; el resto son sobre todo piezas de nave y
  módulos procedurales, que no tienen ficha). Su CDN sirve **WebP de ~12 KB**,
  mucho más ligero que los PNG de 1024 px del juego, y como se descargan a
  local ya no importa que bloquee las peticiones «en caliente» (sí lo hace:
  antes por eso se usaba solo como último recurso). Las URLs resueltas quedan
  cacheadas en `tools/_dl/wiki_icons.json`, que es el mismo fichero que usa
  `tools/build_db.py`, así que nada se pregunta dos veces.

### Iconos en local

`data/icons/` tiene **el catálogo entero** (4 819 imágenes, 219 MB) y el
servidor las sirve en `/icons/…`, así que la interfaz no pide nada a internet:

- 2 096 iconos de la wiki (WebP, ~12 KB cada uno).
- 2 699 del NMS-Handbook (PNG de 1024 px, 74 KB) para lo que la wiki no tiene.
- 24 de Assistant.

`data/icons/map.json` relaciona cada id de objeto con su fichero y con la
fuente; el servidor lo lee al arrancar y cada vez que cambia (un `stat` por
petición), de modo que tras `python tools/fetch_icons.py` los iconos nuevos
aparecen sin reiniciar nada. Si el mapa no está, `db.json` sigue mandando y
todo funciona como antes, con los iconos remotos.

Las dos fuentes no siempre coinciden: al comparar 734 iconos, 80 difieren
(por ejemplo `OXYGEN`, que en la wiki era una molécula gris en lugar del
naranja real, o módulos procedurales con un icono genérico). Aquí manda la
wiki porque es la que está actualizada, pero el Handbook queda como red de
seguridad. Para comparar de nuevo:

```
python tools/fetch_icons.py --no-wiki   # solo Handbook/Assistant
```

El aviso sobre el tamaño: el peso viene casi todo de los PNG del Handbook.
Los de la wiki son 7 veces más pequeños.

### Clase de los módulos

El juego no guarda la clase en el save: se deduce del propio objeto. El
nombre manda cuando lo trae (`B-Class … Upgrade`, `Illegal/Suspicious …`,
`Rusted …`); si no, del sufijo del ID (1=C, 2=B, 3=A, 4=S, X=ilegal,
0=oxidado). Los colores de los distintivos son los de los iconos de módulo
del juego (`proctech.{c,b,a,s,x}.*.png`): C verde, B azul, A rosa, S dorado
y X morado.

---

## Actualizar los datos tras un parche del juego

```
python tools/update_db.py            # todo
python tools/update_db.py --tables   # solo recetas
python tools/update_db.py --lang     # solo textos en español
```

Si no hay conexión, se mantiene lo ya descargado y la herramienta sigue
funcionando. Después de descargar, `data/db.json` se reconstruye solo.

---

## Instalar el ejecutable de Windows

Hay un `.exe` para quien no quiere instalar Python. Se publica como ZIP en las
releases de GitHub.

### Qué se descarga

| | |
| --- | --- |
| Carpeta `NMS Helper` | 29 MB (el `.exe` son 3,8 MB) |
| `NMS Helper-windows.zip` | 13 MB |
| Python necesario | ninguno |
| Iconos del catálogo | no vienen (219 MB): se bajan con «Actualizar datos → Solo iconos» |

Se descomprime en una carpeta cualquiera **donde tengas permisos de
escritura** (por ejemplo `C:\Juegos\NMS Helper`): el programa guarda ahí los
iconos, el `db.json` reconstruido y un `nms_helper.log`.

### «Windows ha protegido tu PC» / el antivirus

El ejecutable **no está firmado** (firmar cuesta un certificado de pago
anual), así que Windows SmartScreen y algunos antivirus avisan. Es lo normal
en programas de código abierto y **no significa que esté infectado**. Para
quitar el aviso:

1. Comprueba la firma del ZIP. En la release hay un `SHA256SUMS.txt`; en
   PowerShell:
   ```powershell
   Get-FileHash .\NMS Helper-windows.zip -Algorithm SHA256
   ```
   Si el resultado no coincide con el publicado, no lo ejecutes.
2. Al descomprimir, los ficheros llevan la marca de bloqueo (vienen de
   internet). Quítasela con:
   ```powershell
   Unblock-File -Path .\NMS Helper\*
   ```
   o con clic derecho → *Propiedades* → *Desbloquear*.
3. Si prefieres no descargar ningún `.exe`, usa `python run.py`: el
   ejecutable es 30 MB de Python empaquetado, y el código fuente son 250 KB.

Para que el programa se empaquete **sin** aparecer en las listas de
detección por heurística (nada de empaquetar con UPX ni de escribir en
%TEMP% al arrancar), que es justo lo que hace el empaquetado de un solo
fichero:

- **carpeta, no un único `.exe`**: un `--onefile` se descomprime en %TEMP%
  cada vez que arranca, y ese patrón es de los que más avisos genera;
- **`--noupx`**: los compresores de binario son la otra causa típica;
- **sin módulos de sobra** dentro (tkinter, PyQt, numpy…): menos DLL que
  escanear;
- **y sin firmar, que es lo único que SmartScreen no perdona** hasta que
  haya certificado.

### Construirlo tú mismo

```
python tools/build_exe.py
```

Crea un entorno virtual aparte con PyInstaller y `pywebview` (son
herramientas de compilación, no dependencias del programa), compila
`nms_helper.spec` y deja en `dist/` la carpeta, el ZIP y el `SHA256SUMS.txt`.
Tarda un par de minutos la primera vez.

### Opciones del arranque

| | |
| --- | --- |
| `python run.py` | ventana de aplicación; navegador si no hay `pywebview` |
| `python run.py --browser` | fuerza el navegador |
| `python run.py --no-browser` | solo el servidor (para pruebas) |
| `python run.py --port 9000` | otro puerto |
| `NMS Helper.exe --tool update_db --icons` | el ejecutable hace de lanzador de las herramientas (así «Actualizar datos» funciona sin Python instalado) |

Para tener la ventana hace falta `pip install pywebview` (usa WebView2, que
ya viene con Windows 10/11 y con Edge). Es **opcional**: sin ella, todo lo
demás funciona igual en el navegador.

---

## Estructura

```
NMS_Helper/
├── run.py                  # punto de entrada (arranca servidor + navegador)
├── nms_helper/
│   ├── save.py             # decodificador LZ4 + desofuscado + inventarios
│   ├── db.py               # carga, consulta y plan de crafteo
│   └── server.py           # API JSON + ficheros estáticos
├── web/
│   ├── index.html
│   ├── style.css
│   ├── app.js
│   ├── favicon.svg
│   └── nms_helper.ico    # icono de la ventana y del ejecutable
├── data/
│   ├── jsonmap.txt         # mapa de claves de los saves
│   ├── db.json             # objetos + recetas (generado)
│   ├── icons/              # iconos del catálogo + map.json (se sirven en /icons/…)
│   └── glyphs/             # los 16 glifos de portal (se sirven en /glyphs/…)
├── tools/
│   ├── _common.py          # rutas de las herramientas (también al empaquetar)
│   ├── update_db.py        # descarga/actualiza las fuentes comunitarias
│   ├── build_db.py         # fusiona las fuentes en data/db.json
│   ├── fetch_icons.py      # baja los iconos del catálogo (wiki primero)
│   ├── fetch_glyphs.py     # baja los 16 glifos de portal a data/glyphs/
│   ├── make_icons.py       # dibuja web/nms_helper.ico con la stdlib
│   ├── build_exe.py        # empaqueta el ejecutable de Windows + SHA-256
│   ├── explore_data.py     # inspección de fuentes (desarrollo)
│   ├── hgpak.py            # lector de los .pak del juego (HGPAK v2)
│   ├── smoke_test.py       # prueba de los endpoints (servidor abierto)
│   └── _dl/                # copia local de las fuentes descargadas
├── nms_helper/
│   ├── paths.py            # dónde está cada carpeta (código o .exe)
│   ├── window.py           # ventana con pywebview/WebView2
│   ├── save.py, db.py, server.py
└── nms_helper.spec         # empaquetado con PyInstaller
```

---

## API

| Ruta | Devuelve |
| --- | --- |
| `GET /api/status` | partidas encontradas (agrupadas en pares y con la más reciente marcada), estado de la base de datos y errores |
| `GET /api/inventory` | inventario completo + totales por objeto + vitales |
| `GET /api/search?q=` | búsqueda de objetos por nombre o ID |
| `GET /api/item/<id>` | ficha: recetas de crafteo, refinado y usos (incluye la clase del módulo) |
| `GET /api/craftable?kind=` | `craft`/`refine`: lo que se puede fabricar o refinar ahora mismo con el inventario (`times` = cuántas veces sale) |
| `GET /api/plan/<id>?n=` | plan de crafteo para `n` unidades: árbol de ingredientes con `via` (fabricar/refinar) y la lista de lo que falta |
| `GET /api/select?i=` | cambia de slot de partida |
| `GET /api/rescan` | vuelve a buscar partidas en disco |
| `GET /api/update/start?what=` | lanza `tools/update_db.py` (`all`/`tables`/`lang`); `409` si ya había una en marcha |
| `GET /api/update/state?since=` | log de la actualización en curso (`lines`, `count`, `running`, `exit`) |

---

## Límites conocidos y siguientes pasos

- **Nombres en inglés en algunos módulos de tecnología procedural**
  (`UP_*`): la base comunitaria no publica esa traducción (sus iconos sí
  se recuperan de la tecnología base a la que mejoran). La solución
  completa es extraer los archivos de idioma del propio juego
  (`GAMEDATA/PCBANKS` → `NMS_LOC1_SPANISH`) con HGPAKTool + MBINCompiler.
- **Módulos de corbeta sin nombre** (`CV_FIT*`, `CV_INV*`, `CV_SCI*`,
  `CV_TRA*`): todas las fuentes tienen la misma clave de localización sin
  traducir (`UT_CR_*_NAME_L`) y ninguna la resuelve (ni el Handbook ni los
  archivos de idioma que publica la wiki del juego). Se muestran por su ID,
  pero **con icono y clase**, y se puede pulsar su ficha.
- **Taller de corbetas**: la sección `CorvetteStorageInventory` queda fuera
  de la interfaz (no hace falta para esta herramienta). Allí solo estaban
  `B_DECO_M` (ya con icono) y `B_MAG_1X1`, que no aparece en ninguna de las
  cuatro bases comunitarias.
- **Ranuras con id ilegible**: dos ranuras del carguero guardan bytes que no
  son UTF-8 válido (están igual en `save.hg` y en `save2.hg`, así que no es
  un fallo de lectura). Se conservan en el inventario como «objeto
  desconocido» en vez de ocultarlos.
- **Descripciones**: los iconos que el juego incrusta en el texto se
  muestran como `[icono]` / `[icon]`, ya que esos sprites no están en
  ninguna fuente comunitaria.
- **Base de datos local**: hoy la fuente primaria es la comunitaria; la
  extracción directa de tus `.pak` queda como segunda opción para que la
  herramienta siga funcionando si una fuente comunitaria cambia de formato.
  Esa extracción ya tiene la primera pieza escrita
  (`tools/hgpak.py`, reimplementación MIT de HGPAKtool): con ella se leen los
  `.pak` del juego y están localizados los textos de idioma, que viven en
  `NMSARC.MetadataEtc.pak` → `language/nms_loc1_spanish.mbin` (y
  `nms_loc1_latinamericanspanish.mbin`, más las tablas `loc4`, `loc5` y
  `update3`, en 17 idiomas). ahí está justo lo que faltaba: los nombres de los
  módulos procedurales (`UP_SHIPSHOT_*`, en `nms_loc4`). Queda pendiente
  emparejar cada clave con su frase (el archivo es un array de registros de
  0x130 con la clave en línea y detrás una lista de cadenas, más un puntero
  a un diccionario de palabras) y escribir el lector de MBIN que falta.
  Además hace
  falta `zstandard` para descomprimir: Python 3.12 no trae ZSTD en la stdlib
  (llega en 3.14), y como es un paso de compilación, no afecta a la app.
  Los módulos de corbeta (`CV_*`, claves `UT_CR_*_NAME_L`) **no** están en
  ninguna tabla de idioma, así que ese hueco no se puede cerrar por aquí.
- **Modo de partida**: el nombre del modo sale del mapa de claves en
  español («Supervivencia»), así que no se traduce al cambiar a `EN`. La
  ubicación (`SaveSummary`) y los nombres de las naves son datos del
  guardado: van tal cual.
- Ideas pendientes: alertas (combustible, tecnología dañada) y tabla de
  refinadoras filtrable con cálculo de operaciones/tiempo.
- **Líneas ley**: la calculadora es la de la comunidad, y sus resultados
  solo son fiables entre 45°N y 45°S. La escala (unidades por grado) sale de
  tus propias dos lecturas tratando los grados como si fueran planos, así
  que el «navegador» es una aproximación: úsalo para orientarte y luego
  busca a ojo. En el save **no** hay lat/long del planeta (el juego no las
  guarda), así que hay que leerlas del visor de análisis; hacerlo a mano es
  lo previsto, leerlas en tiempo real solo sería posible con OCR de pantalla
  (experimental) o leyendo la memoria del juego (reverse engineering por
  parche, no recomendado).

---

## Licencia

MIT (ver [`LICENSE`](LICENSE)). El código es de Caspian; los datos, nombres
e iconos vienen de la base comunitaria que se cita arriba (nmstoolkit,
NMS-Handbook, Assistant, la wiki y el decodificador de portales), y las
fórmulas del conversor de direcciones y de la calculadora de líneas ley están
reimplementadas a partir de
[NMSCD/Coordinate-Conversion](https://github.com/NMSCD/Coordinate-Conversion)
y [NMSCD/leylinecalc](https://github.com/NMSCD/leylinecalc), ambas MIT.

---

## Requisitos

- Python 3.10 o superior (probado con 3.12).
- No Man's Sky instalado y al menos una partida guardada.
