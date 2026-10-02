/* Modo de ejecución de la interfaz.
   false = programa local (run.py o .exe): detrás está el servidor Python.
   true  = sitio estático publicado en GitHub Pages: no hay servidor, así que
   web/static-db.js contesta las rutas /api/* con data/db.json en el
   navegador. tools/build_site.py escribe `true` al montar site/; este
   fichero del repositorio se queda en `false` para el programa local. */
window.NMS_STATIC = false;
