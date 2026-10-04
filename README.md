# Catálogo Web - Bar Papelería

Sitio web estático para **Bar Papelería**, un emprendimiento de papelería personalizada.

El objetivo del sitio es mostrar productos, servicios y trabajos realizados, permitiendo que los clientes puedan conocer la propuesta del emprendimiento y contactarse fácilmente para realizar consultas o pedidos.

## Descripción

Este proyecto corresponde a un catálogo web simple desarrollado con tecnologías básicas de frontend:

* HTML
* CSS
* Imágenes estáticas

El sitio está pensado para ser liviano, rápido y fácil de publicar en plataformas gratuitas como **Netlify**.

Sitio publicado: https://bar-papeleria.netlify.app/

## Secciones de la página

Pensada principalmente para celulares, de arriba hacia abajo:

1. **Encabezado fijo:** logo, botón de Instagram (`@bar.papeleria`) y botón de pedido por WhatsApp.
2. **Tarjeta estilo perfil de Instagram:** cuenta verificada, publicaciones, seguidores, sucursales y botón "Seguir en Instagram".
3. **Título y botón "Ver catálogo PDF".**
4. **Categorías:** accesos rápidos a Cumpleaños, Emprendimientos, Servicios rápidos, Combos y Mis trabajos.
5. **Productos con precios** (Cumpleaños y eventos, Emprendimientos), **Servicios rápidos**, **Combos** y **Mis trabajos**.
6. **Llamado final** para enviar los datos del pedido por WhatsApp.
7. **Footer:** sucursales, envíos y botones de Instagram y WhatsApp.

Además hay un botón flotante de WhatsApp y otro para volver arriba.

Todos los botones de pedido abren WhatsApp con un mensaje ya armado (número configurado en `WHATSAPP_PHONE`, dentro del `<script>` de `public/index.html`).

## Estructura del proyecto

Todo lo que se publica en el sitio está en la carpeta `public/`. El resto del repositorio (documentación y scripts) es interno y **no** se publica.

```txt
/
├── public/                   ← lo único que publica Netlify
│   ├── index.html
│   ├── estilos.css
│   ├── favicon.ico
│   ├── _headers              (cacheo de imágenes en Netlify)
│   ├── pdf/
│   │   └── catalogo-bar-papeleria.pdf
│   └── img/
│       ├── logo-bar.webp
│       ├── logo-bar-sm.webp
│       ├── og-image.jpg      (imagen de vista previa al compartir el link)
│       ├── favicon-32.png
│       ├── apple-touch-icon.png
│       ├── banderines-1.webp
│       ├── ...
│       ├── md/               (versiones medianas para celulares)
│       └── thumbs/           (miniaturas de las galerías)
├── tools/                    (scripts internos, no se publican)
│   ├── generar_catalogo_pdf.py
│   └── optimizar_imagenes.py
├── netlify.toml              (le indica a Netlify que publique public/)
├── README.md
└── CLAUDE.md                 (instrucciones para trabajar con Claude Code)
```

## Contenido del sitio

El catálogo incluye productos y trabajos relacionados con papelería personalizada, como por ejemplo:

* Souvenirs personalizados
* Centros de mesa
* Servilleteros
* Candy bar para cumpleaños
* Libritos para colorear
* Banderines
* Toppers para tortas y cupcakes
* Stickers
* Stickers para lápices
* Tatuajes temporales
* Letras 3D
* Tarjetas para emprendimientos
* Volantes
* Fotos impresas
* Fotos estilo Polaroid
* Fotocopias
* Impresiones en blanco y negro
* Anillados

También se ofrecen trabajos pensados para:

* Cumpleaños
* Emprendimientos
* Eventos
* Regalos personalizados
* Detalles temáticos
* Decoración

## Tecnologías utilizadas

* HTML5
* CSS3
* Imágenes locales
* Hosting estático mediante Netlify

## Cómo ejecutar el sitio localmente

No se requiere instalación de dependencias.

Para ver el sitio en una computadora local:

1. Descargar o clonar el repositorio.
2. Abrir el archivo `public/index.html` en el navegador.

También se puede usar la extensión **Live Server** de Visual Studio Code: hacer clic derecho sobre `public/index.html` → "Open with Live Server".

Otra opción, desde la raíz del repositorio:

```bash
python -m http.server 5500 --directory public
```

y abrir http://localhost:5500

## Imágenes

Las fotos del sitio están optimizadas en formato **WebP** para que la página cargue rápido en celulares:

* `public/img/<nombre>.webp`: versión grande (máx. 1200 px), para pantallas grandes.
* `public/img/md/<nombre>.webp`: versión mediana (máx. 800 px), la que bajan la mayoría de los celulares.
* `public/img/thumbs/<nombre>.webp`: miniatura (máx. 400 px) para las galerías.
* `public/img/logo-bar-sm.webp`: logo chico para el encabezado y el pie.
* Las imágenes principales usan `srcset` + `sizes`: el navegador elige solo el tamaño justo para cada pantalla.
* Todas las imágenes usan `loading="lazy"`: se descargan recién cuando el usuario llega a esa parte de la página.

Para agregar una foto nueva:

1. Copiar la foto (`.jpg` o `.png`) en `public/img/`.
2. Correr el optimizador, que genera las tres versiones (grande, mediana y miniatura) y borra la foto original. No toca `og-image.jpg` ni los favicons, que tienen que quedar en JPG/PNG:

```bash
python tools/optimizar_imagenes.py
```

3. En `public/index.html`, copiar el bloque de un producto existente y cambiar el nombre de la foto en todas sus rutas (`src`, `srcset`, `data-full` y `data-srcset`). Los números con `w` del `srcset` son el ancho real de cada archivo en píxeles.

## Tarjeta de Instagram: actualizar los números

Las publicaciones y seguidores de la tarjeta del inicio **están escritos a mano** (Instagram no permite leerlos automáticamente desde una página estática). Están redondeados con "+" para que sigan siendo correctos por meses, por ejemplo `+140` y `+1.100`.

Cuando el perfil crezca, actualizarlos en `public/index.html` buscando el comentario:

```html
<!-- Números redondeados a mano: actualizarlos cada tanto desde el perfil de Instagram. -->
```

## Google y vista previa al compartir

En el `<head>` de `public/index.html` están:

* `meta name="description"`: el texto que Google muestra debajo del título en los resultados.
* Etiquetas `og:` (Open Graph): la tarjeta que aparece al compartir el link por WhatsApp, Instagram o Facebook, con la imagen `public/img/og-image.jpg` (1200×630 px).
* Favicon (`public/favicon.ico`, `public/img/favicon-32.png` y `public/img/apple-touch-icon.png`).
* Datos estructurados (`<script type="application/ld+json">`, formato schema.org): describen a Google el negocio, las sucursales de Florencio Varela y Lanús, el teléfono y el Instagram. Si cambian esos datos, actualizarlos también ahí.

Si cambia la descripción del negocio (sucursales, productos, envíos), conviene actualizar `description` y `og:description` juntos. WhatsApp guarda en caché las vistas previas, así que en chats donde ya se compartió el link puede tardar en verse la nueva.

## Google Analytics

Para que no compita con la carga inicial, el script de Google Analytics se descarga al primer scroll o toque del visitante (o a los 8 segundos si no hay interacción). Los eventos que ocurren antes quedan en cola y se envían igual.

Eventos que registra el sitio:

* `click_whatsapp`: clic en cualquier botón de WhatsApp, con la sección y el producto.
* `click_instagram`: clic en Instagram (`header`, `tarjeta hero` o `footer`).
* `click_catalogo_pdf`: clic en "Ver catálogo PDF".

Se ven en Google Analytics en **Informes → Interacción → Eventos**.

## Catálogo PDF

El botón **Ver catálogo PDF** abre `public/pdf/catalogo-bar-papeleria.pdf`. Ese archivo se genera automáticamente a partir de `public/index.html` (productos, precios, servicios y combos), así que después de cambiar precios en la web hay que regenerarlo:

```bash
python tools/generar_catalogo_pdf.py
```

Requiere Python 3 con Pillow (`pip install pillow`) y Google Chrome o Microsoft Edge instalados.

Los pasos de "Cómo hacer un pedido" que aparecen en el PDF están en la constante `STEPS` del generador (esa sección ya no está en la web).

## Publicación

El sitio está preparado para ser publicado como sitio estático en Netlify.

La configuración está en `netlify.toml`, en la raíz del repositorio, y tiene prioridad sobre lo configurado en el panel de Netlify:

```toml
[build]
  publish = "public"
```

No hay comando de build: Netlify publica la carpeta `public/` tal cual. Cada push a `main` se publica automáticamente en unos segundos.

## Recomendaciones

Para mantener buen rendimiento del sitio:

* Pasar las fotos nuevas por `tools/optimizar_imagenes.py` antes de subirlas.
* No agregar scripts externos ni widgets pesados sin medir el impacto.
* Revisar el sitio en [PageSpeed Insights](https://pagespeed.web.dev/) después de cambios grandes.
* Mantener nombres de archivos simples, sin espacios ni caracteres especiales.
* Revisar que las rutas de las imágenes coincidan exactamente con los nombres reales de los archivos.

## Estado del proyecto

Sitio publicado y en uso. Resultados de PageSpeed Insights (octubre 2026): 100 en rendimiento, accesibilidad, buenas prácticas y SEO, tanto en celular como en computadora.

Ya implementado:

* Pedidos por WhatsApp con mensaje armado y botón flotante.
* Navegación rápida por categorías.
* Imágenes optimizadas (WebP, tamaños por pantalla y carga diferida).
* Catálogo PDF generado desde la web.
* Tarjeta y botones de Instagram.
* Descripción para Google, vista previa al compartir y favicon.

Posibles mejoras futuras:

* Actualización automática de los números de Instagram (requiere la API de Meta y una función de Netlify).
* Catálogo dinámico desde archivo JSON.
* Dominio propio.
* Panel simple de administración.

## Autoría

Sitio desarrollado para el emprendimiento **Bar Papelería**.
