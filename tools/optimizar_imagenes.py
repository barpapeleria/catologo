"""
Optimiza las imágenes de public/img/ para que el sitio cargue rápido en celulares.

Por cada foto .jpg/.jpeg/.png que encuentra en public/img/ genera:
  - public/img/<nombre>.webp         versión grande (máx. 1200 px de lado, WebP calidad 82)
  - public/img/md/<nombre>.webp      versión mediana para celulares (máx. 800 px, calidad 82)
  - public/img/thumbs/<nombre>.webp  miniatura para las galerías (máx. 400 px, calidad 78)
y borra la foto original (queda guardada en el historial de git).

Las fotos que ya están en .webp no se tocan, así que se puede correr las veces
que haga falta. Tampoco toca los archivos de KEEP_AS_IS (og-image.jpg y los
favicons), que tienen que quedar en JPG/PNG. Para sumar una foto nueva: copiarla en public/img/, correr el script y
usar el .webp en public/index.html.

Uso (desde la raíz del repo):
    python tools/optimizar_imagenes.py

Requiere: Python 3 y Pillow.
"""

from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "public" / "img"  # carpeta que publica Netlify
MD = IMG / "md"
THUMBS = IMG / "thumbs"

FULL_SIZE, FULL_QUALITY = 1200, 82
MD_SIZE, MD_QUALITY = 800, 82
THUMB_SIZE, THUMB_QUALITY = 400, 78
SOURCES = {".jpg", ".jpeg", ".png"}

# Archivos que tienen que quedar en JPG/PNG (vista previa al compartir y
# favicons): WhatsApp, redes y celulares no siempre aceptan WebP.
KEEP_AS_IS = {"og-image.jpg", "favicon-32.png", "apple-touch-icon.png"}


def load(path):
    with Image.open(path) as im:
        im = ImageOps.exif_transpose(im)
        im.load()
    # Solo se conserva la transparencia si realmente hay píxeles transparentes.
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        if im.getchannel("A").getextrema()[0] == 255:
            im = im.convert("RGB")
    else:
        im = im.convert("RGB")
    return im


def save(im, path, size, quality):
    copy = im.copy()
    copy.thumbnail((size, size), Image.LANCZOS)
    copy.save(path, "WEBP", quality=quality, method=6)
    return path.stat().st_size


def main():
    MD.mkdir(exist_ok=True)
    THUMBS.mkdir(exist_ok=True)
    sources = sorted(p for p in IMG.iterdir()
                     if p.is_file() and p.suffix.lower() in SOURCES and p.name not in KEEP_AS_IS)
    if not sources:
        print("No hay imágenes nuevas para optimizar.")
        return

    before = after = 0
    for src in sources:
        im = load(src)
        full = save(im, IMG / f"{src.stem}.webp", FULL_SIZE, FULL_QUALITY)
        save(im, MD / f"{src.stem}.webp", MD_SIZE, MD_QUALITY)
        thumb = save(im, THUMBS / f"{src.stem}.webp", THUMB_SIZE, THUMB_QUALITY)
        size = src.stat().st_size
        before += size
        after += full
        print(f"  {src.name:40} {size / 1024:7.0f} KB -> {full / 1024:5.0f} KB (miniatura {thumb / 1024:.0f} KB)")
        src.unlink()

    print(f"\n{len(sources)} imágenes: {before / 1048576:.1f} MB -> {after / 1048576:.1f} MB "
          f"({100 - after * 100 / before:.0f}% menos)")
    print("Recordá usar los .webp en index.html (ver la sección Imágenes del README).")


if __name__ == "__main__":
    main()
