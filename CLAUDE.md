# CLAUDE.md — Catálogo web de Bar Papelería

Instrucciones para trabajar en este proyecto. Complementa al `README.md`, que explica el sitio para personas; este archivo explica **cómo trabajar** en él.

## Contexto

- Catálogo web estático (HTML + CSS + JS sin frameworks) de **Bar Papelería**, papelería personalizada con sucursales en **Florencio Varela (La Sirena)** y **Lanús**, y envíos a todo el país.
- Publicado en Netlify: https://bar-papeleria.netlify.app/ (publica solo la carpeta `public/`, sin build, desde la rama `main`; configurado en `netlify.toml`).
- Lo mantienen **Fernando** (parte técnica) y **Barby** (dueña del negocio, decide diseño y contenido).
- Las clientas entran **casi siempre desde el celular**, sobre todo a partir del link compartido por WhatsApp e Instagram.
- Instagram: `@bar.papeleria` (cuenta verificada). WhatsApp: `+54 9 11 3891-9650`.

## Comunicación

- Responder siempre en **español rioplatense** (vos, tocá, mirá).
- Cuando pidan explicar algo "para Barby", hacerlo sin tecnicismos, con ejemplos cotidianos.
- En cambios visuales, **mostrar cómo queda antes de hacer commit** (captura en tamaño celular).
- Ante una decisión de diseño con varias opciones, dar una recomendación clara y el porqué.

## Git: commits y push

- **Nunca** agregar `Co-Authored-By: Claude` ni ninguna mención de co-autoría o atribución a Claude en commits ni en PRs.
- Hacer commit y push **solo cuando lo pidan**. Se trabaja directo sobre `main`.
- Antes de commitear: `git fetch` y comprobar que `main` no esté atrasada respecto de `origin/main`.
- Mensajes en español, **bien detallados**, con este formato de título:
  - `(feat-descripcion-corta): qué se hizo` para funcionalidades y cambios visuales.
  - `(docs-xxx): ...` para documentación.
- El cuerpo del mensaje explica el motivo, cada cambio por archivo y qué se verificó (anchos probados, PageSpeed, etc.).
- La identidad de git del repo es `Bar Papeleria <bar.papeleria@gmail.com>`; no cambiarla.
- Después del push, esperar a que Netlify publique (unos 20 segundos) y verificar con `curl` que el cambio esté online.

## Estructura

**Todo lo que se publica vive en `public/`.** El resto del repo es interno y Netlify no lo sirve: nunca poner archivos del sitio fuera de `public/`, ni archivos internos (notas, scripts, documentos) dentro de `public/`.

```txt
public/                          ← lo único que publica Netlify
  index.html                     Página única: HTML, JSON-LD y el <script> con WhatsApp, galerías y Analytics
  estilos.css                    Todos los estilos (variables en :root)
  _headers                       Netlify: caché de 7 días para /img/*
  favicon.ico
  pdf/catalogo-bar-papeleria.pdf Catálogo PDF (se genera, no se edita a mano)
  img/<nombre>.webp              Foto grande (máx. 1200 px)
  img/md/<nombre>.webp           Foto mediana (máx. 800 px), la que bajan los celulares
  img/thumbs/<nombre>.webp       Miniatura (máx. 400 px), para las galerías
  img/logo-bar-sm.webp           Logo chico (encabezado, footer, tarjeta de Instagram)
  img/og-image.jpg               Vista previa al compartir el link (1200x630); debe quedar en JPG
  img/favicon-32.png, img/apple-touch-icon.png   Favicons; deben quedar en PNG
tools/generar_catalogo_pdf.py    Genera public/pdf/... leyendo public/index.html
tools/optimizar_imagenes.py      Convierte fotos nuevas de public/img/ a WebP en 3 tamaños
netlify.toml                     [build] publish = "public"
README.md, CLAUDE.md             Documentación (no se publica)
```

## Orden de la página (no cambiar sin que lo pidan)

1. Encabezado fijo: logo, botón de Instagram y botón "Hacer pedido"/"Pedir" (WhatsApp).
2. Hero: tarjeta estilo perfil de Instagram (`#heroInstagramCard`), título `h1` rosa, subtítulo y botón "Ver catálogo PDF".
3. Categorías (`nav.categories`): Cumpleaños, Emprendimientos, Servicios rápidos, Combos, Mis trabajos. **Son la navegación principal hacia los precios; siempre deben quedar.**
4. Secciones: `#cumples`, `#emprendimientos`, `#servicios-rapidos`, `#combos`, `#mis-trabajos`.
5. Llamado final (`.final-cta`) y footer con sucursales y botones de Instagram y WhatsApp.
6. Botón flotante de WhatsApp (`#floating`) y botón para volver arriba.

Secciones que se **eliminaron a pedido** y no hay que volver a agregar: "Especial Mundial" y su botón, "Trabajos pensados para", "Lista rápida de precios" y "Cómo hacer un pedido".

## Diseño

- Variables en `:root` de `estilos.css`: `--primary` (#e85d9e), `--primary-dark` (#b92f72), `--violet`, `--green` (#25d366), `--green-text` (#073b1f), `--brand-gradient` (rosa #e3157f a #c2116b), `--border`, `--muted`, `--text`.
- Tipografía: Arial/Helvetica del sistema. No agregar fuentes web.
- **Botones de WhatsApp:** fondo verde WhatsApp `var(--green)` con **texto oscuro** `var(--green-text)` (contraste 6,4:1) e ícono de WhatsApp. No volver al texto blanco: falla en accesibilidad.
- **Ícono de WhatsApp:** está definido una sola vez como `<symbol id="icon-whatsapp">` al inicio del `<body>`. Para usarlo en un botón nuevo:
  ```html
  <svg class="wa-icon" aria-hidden="true"><use href="#icon-whatsapp"/></svg>
  ```
- **Instagram:** degradé `linear-gradient(45deg, #d62976, #c13584 45%, #833ab4)` con texto blanco.
- **Título `h1`:** rosa con `--brand-gradient` (`background-clip: text`). En celular (≤ 700 px) va **en una sola fila**: `.hero` tiene `container-type: inline-size` y el tamaño se calcula con `calc(min(100cqi, 420px) / 33.8)` para que la frase ocupe el ancho de la tarjeta. Si se cambia el texto del título, recalibrar el divisor.
- `html` tiene `scroll-padding-top: 110px` para que, al tocar una categoría, el título de la sección no quede tapado por el encabezado fijo.
- No usar emojis dentro del catálogo PDF (hacen lento el render en celulares). En la web sí se pueden usar.

## Celular primero: cómo probar

- Probar siempre en **360, 384 y 412 px de ancho** (384–412 px son los Samsung S24 Ultra y S25 Ultra que usan para probar) y en escritorio.
- Verificar que nada se desborde (`document.documentElement.scrollWidth > innerWidth`), que no haya anclas `#` rotas y que las imágenes carguen.
- Para la vista previa local: servidor estático `python -m http.server 5510 --directory public` (con `.claude/launch.json` temporal) y emulación de celular en el navegador. En VS Code, Live Server se abre sobre `public/index.html`. Al terminar, **borrar** `.claude/` y cualquier archivo temporal de prueba para no commitearlos (usan GitHub Desktop, que muestra todo lo que queda en la carpeta).
- El navegador cachea `estilos.css`: recargar con Ctrl + Shift + R o pedir los archivos con `fetch(..., { cache: 'reload' })`.

## Rendimiento (PageSpeed: hoy 100 en las 4 categorías, celular y computadora)

- No agregar scripts externos, widgets, videos ni fuentes web sin medir el impacto.
- **Google Analytics está diferido a propósito**: se carga al primer scroll/toque o a los 8 s del load. No volver a ponerlo en el `<head>` con `async`.
- Todas las imágenes llevan `loading="lazy"` y `decoding="async"`, salvo el logo del encabezado.
- Las fotos principales usan `srcset` (md 800w + grande 1200w, con el ancho real de cada archivo) y `sizes`. En las tarjetas de producto, `sizes` se calcula según la proporción de la foto, porque se muestra con `object-fit: contain` en un recuadro 16:11.
- Las miniaturas de las galerías llevan `data-full`, `data-srcset` y `data-sizes`; el JS de la galería los copia al `.main-img` al tocarlas.
- Después de cambios grandes, medir en https://pagespeed.web.dev/ (celular y computadora). Para medir antes de publicar: `npx lighthouse <url> --form-factor=mobile --throttling-method=devtools`. Contra `localhost` con throttling simulado siempre da 100 y no sirve para comparar.

## Tareas frecuentes

### Cambiar precios
1. Editar el precio en la tarjeta del producto en `public/index.html`: el `<strong class="price">` y, si tiene variantes, los `<li>x30: ...</li>`.
2. Regenerar el PDF: `python tools/generar_catalogo_pdf.py`.
3. Verificar que los precios del PDF coincidan con los de la web.

### Agregar una foto nueva
1. Copiar la foto `.jpg` o `.png` en `public/img/`.
2. `python tools/optimizar_imagenes.py`: genera grande, mediana y miniatura en WebP y borra el original. Ignora los archivos de `KEEP_AS_IS` (`og-image.jpg` y favicons), que deben quedar en JPG/PNG; si se agrega otro archivo de ese tipo, sumarlo a esa lista.
3. En `public/index.html`, copiar el bloque de un producto existente y cambiar el nombre en `src`, `srcset`, `data-full` y `data-srcset`, con los anchos reales (`w`) de cada archivo.

### Actualizar los números de Instagram
Están escritos a mano en la tarjeta del hero, redondeados con "+" (por ejemplo `+140` publicaciones y `+1.100` seguidores). Buscar en `public/index.html` el comentario "Números redondeados a mano". No mostrar "seguidos" ni la cuenta personal.

### Cambiar datos del negocio (sucursales, teléfono, descripción)
Actualizar juntos, para que coincidan:
- `meta name="description"` y `og:description`.
- El JSON-LD (`<script type="application/ld+json">`, tipo `Store`).
- La bio de la tarjeta de Instagram y el footer.
- La imagen `public/img/og-image.jpg`, si cambia algo de lo que muestra.
- `WHATSAPP_PHONE` en el `<script>` si cambia el número.

### Catálogo PDF
- `tools/generar_catalogo_pdf.py` lee productos, precios, servicios y combos de `public/index.html` y lo imprime con Chrome/Edge headless.
- Los pasos de "Cómo hacer un pedido" del PDF están en la constante `STEPS` del generador (esa sección ya no está en la web).
- Para revisar el PDF visualmente, usar PyMuPDF instalado en una carpeta temporal (`pip install --target <temp> pymupdf`), no en el sistema.

## Google Analytics

Eventos que registra el sitio (no renombrarlos, se usan para medir resultados):
- `click_whatsapp`: cualquier link a `wa.me`, con `categoria` (sección) y `producto`. Los botones especiales se identifican por id: `topWhatsappButton` (Header), `finalWhatsappButton` (CTA final), `footerWhatsappButton` (Footer), `floating` (botón flotante).
- `click_instagram`: con `ubicacion` `header`, `tarjeta hero` o `footer`.
- `click_catalogo_pdf`.

## Detalles técnicos a tener en cuenta

- Varios archivos (por ejemplo `public/estilos.css` y `tools/*.py`) tienen finales de línea CRLF en la copia de trabajo (el repo guarda LF). Al editar con scripts, conservar los finales de línea de cada archivo.
- Si Windows no deja mover o renombrar una carpeta ("Permission denied"), suele ser porque VS Code/Live Server o el Explorador la tienen abierta: mover los archivos de a uno o cerrar esos programas.
- Netlify sirve con caché de 7 días las imágenes (`public/_headers`): si se reemplaza una foto **con el mismo nombre**, algunos visitantes pueden ver la vieja. Mejor usar un nombre nuevo.
- La herramienta OpenSpec se evaluó y se descartó para este proyecto: es chico y los cambios se deciden mirando el resultado.

## Pendientes y posibles mejoras

- Dominio propio (por ejemplo `barpapeleria.com.ar`), registrado en NIC Argentina y conectado a Netlify. Lo hacen más adelante.
- Perfil de Empresa en Google para cada sucursal (lo crean ellos).
- Revisar en Google Analytics cómo evolucionan los clics de WhatsApp tras el cambio de los botones (texto oscuro e ícono).
- Opcional: números de Instagram automáticos con la API de Meta y una función de Netlify.
