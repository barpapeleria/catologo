# Catálogo Web - Bar Papelería

Sitio web estático para **Bar Papelería**, un emprendimiento de papelería personalizada.

El objetivo del sitio es mostrar productos, servicios y trabajos realizados, permitiendo que los clientes puedan conocer la propuesta del emprendimiento y contactarse fácilmente para realizar consultas o pedidos.

## Descripción

Este proyecto corresponde a un catálogo web simple desarrollado con tecnologías básicas de frontend:

* HTML
* CSS
* Imágenes estáticas

El sitio está pensado para ser liviano, rápido y fácil de publicar en plataformas gratuitas como **Netlify**.

## Estructura del proyecto

```txt
/
├── index.html
├── estilos.css
├── README.md
├── _headers                  (cacheo de imágenes en Netlify)
├── pdf/
│   └── catalogo-bar-papeleria.pdf
├── tools/
│   ├── generar_catalogo_pdf.py
│   └── optimizar_imagenes.py
└── img/
    ├── logo-bar.webp
    ├── banderines-1.webp
    ├── ...
    └── thumbs/               (miniaturas de las galerías)
        ├── banderines-1.webp
        └── ...
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
2. Abrir el archivo `index.html` en el navegador.

También se puede usar la extensión **Live Server** de Visual Studio Code para trabajar de forma más cómoda.

## Imágenes

Las fotos del sitio están optimizadas en formato **WebP** para que la página cargue rápido en celulares:

* `img/<nombre>.webp`: versión grande (máx. 1200 px), la que se ve en cada producto.
* `img/thumbs/<nombre>.webp`: miniatura (máx. 400 px) para las galerías, servicios y logo.
* Todas las imágenes usan `loading="lazy"`: se descargan recién cuando el usuario llega a esa parte de la página.

Para agregar una foto nueva:

1. Copiar la foto (`.jpg` o `.png`) en `img/`.
2. Correr el optimizador, que genera el `.webp` y la miniatura y borra la foto original:

```bash
python tools/optimizar_imagenes.py
```

3. En `index.html` usar `./img/<nombre>.webp` para la imagen principal y, en las galerías, `./img/thumbs/<nombre>.webp` con `data-full="./img/<nombre>.webp"`.

## Catálogo PDF

El botón **Ver catálogo PDF** abre `pdf/catalogo-bar-papeleria.pdf`. Ese archivo se genera automáticamente a partir de `index.html` (productos, precios, servicios y combos), así que después de cambiar precios en la web hay que regenerarlo:

```bash
python tools/generar_catalogo_pdf.py
```

Requiere Python 3 con Pillow (`pip install pillow`) y Google Chrome o Microsoft Edge instalados.

## Publicación

El sitio está preparado para ser publicado como sitio estático en Netlify.

Configuración recomendada en Netlify:

```txt
Build command: dejar vacío
Publish directory: /
```

Si los archivos se suben dentro de una carpeta contenedora, el `Publish directory` debe apuntar a esa carpeta.

## Recomendaciones

Para mantener buen rendimiento del sitio:

* Optimizar las imágenes antes de subirlas.
* Usar imágenes en formato `.webp` cuando sea posible.
* Evitar imágenes demasiado pesadas.
* Mantener nombres de archivos simples, sin espacios ni caracteres especiales.
* Revisar que las rutas de las imágenes coincidan exactamente con los nombres reales de los archivos.

## Estado del proyecto

Proyecto en desarrollo inicial.

El sitio puede evolucionar en futuras versiones incorporando:

* Catálogo dinámico desde archivo JSON
* Filtros por categoría
* Botón de pedido por WhatsApp
* Dominio propio
* Panel simple de administración
* Integración con formularios de contacto

## Autoría

Sitio desarrollado para el emprendimiento **Bar Papelería**.
