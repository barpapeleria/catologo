"""
Genera pdf/catalogo-bar-papeleria.pdf a partir de index.html.

Lee productos, precios, servicios, combos y pasos directamente del HTML del
sitio, así el PDF queda siempre igual que la web. Achica las imágenes y usa
Chrome/Edge en modo headless para imprimir el PDF.

Uso (desde la raíz del repo):
    python tools/generar_catalogo_pdf.py

Requiere: Python 3, Pillow y Google Chrome o Microsoft Edge instalados.
"""

import datetime
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
OUTPUT = ROOT / "pdf" / "catalogo-bar-papeleria.pdf"

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

BROWSERS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "google-chrome", "chromium", "chromium-browser", "microsoft-edge",
]


# ---------------------------------------------------------------------------
# Lectura de index.html
# ---------------------------------------------------------------------------

def text(fragment):
    """Saca etiquetas, decodifica entidades y normaliza espacios."""
    fragment = re.sub(r"<[^>]+>", " ", fragment or "")
    return re.sub(r"\s+", " ", html.unescape(fragment)).strip()


def first(pattern, source, default=""):
    match = re.search(pattern, source, re.S)
    return text(match.group(1)) if match else default


def section(source, section_id):
    match = re.search(r'<section[^>]*id="%s"[^>]*>(.*?)</section>' % section_id, source, re.S)
    if not match:
        sys.exit(f"No encontré la sección #{section_id} en index.html")
    return match.group(1)


def first_img(fragment):
    match = re.search(r'<img[^>]*class="[^"]*(?:main-img|combo-card__image)[^"]*"[^>]*src="([^"]+)"', fragment, re.S) \
        or re.search(r'<img[^>]*src="([^"]+)"', fragment, re.S)
    return match.group(1) if match else ""


def parse_products(source, section_id):
    products = []
    for card in re.findall(r"<article[^>]*class=\"card[^\"]*\"[^>]*>(.*?)</article>", section(source, section_id), re.S):
        main = first_img(card)
        products.append({
            "name": first(r"<h3>(.*?)</h3>", card),
            "price": first(r'<strong class="price">(.*?)</strong>', card),
            "pill": first(r'<span class="pill">(.*?)</span>', card),
            "desc": first(r"</h3>\s*<p>(.*?)</p>", card),
            "items": [text(li) for li in re.findall(r"<li>(.*?)</li>", card, re.S)],
            "img": main,
        })
    return products


def parse_services(source):
    services = []
    for art in re.findall(r"<article>(.*?)</article>", section(source, "servicios-rapidos"), re.S):
        services.append({
            "name": first(r"<h3>(.*?)</h3>", art),
            "desc": first(r"</h3>\s*<p>(.*?)</p>", art),
            "img": first_img(art),
        })
    return services


def parse_combos(source):
    combos = []
    for art in re.findall(r'<article class="combo-card[^"]*">(.*?)</article>', section(source, "combos"), re.S):
        combos.append({
            "label": first(r'<p class="combo-card__label">(.*?)</p>', art),
            "name": first(r"<h3>(.*?)</h3>", art),
            "items": [text(li) for li in re.findall(r"<li>(.*?)</li>", art, re.S)],
            "img": first_img(art),
        })
    return combos


def parse_steps(source):
    steps = []
    for art in re.findall(r"<article>(.*?)</article>", section(source, "como-pedir"), re.S):
        steps.append({
            "num": first(r"<span>(.*?)</span>", art),
            "name": first(r"<h3>(.*?)</h3>", art),
            "desc": first(r"<p>(.*?)</p>", art),
        })
    return steps


def parse_phone(source):
    match = re.search(r"WHATSAPP_PHONE\s*=\s*'(\d+)'", source)
    if not match:
        sys.exit("No encontré WHATSAPP_PHONE en index.html")
    return match.group(1)


def pretty_phone(phone):
    # 5491138919650 -> +54 9 11 3891-9650
    if len(phone) == 13 and phone.startswith("549"):
        return f"+54 9 {phone[3:5]} {phone[5:9]}-{phone[9:]}"
    return "+" + phone


# ---------------------------------------------------------------------------
# Imágenes
# ---------------------------------------------------------------------------

def make_thumb(src, workdir, size):
    """Copia la imagen achicada (recorte cuadrado/proporcional) y devuelve su URI."""
    if not src:
        return ""
    path = (ROOT / src).resolve()
    if not path.exists():
        print(f"  ! Falta la imagen {src}")
        return ""
    out = workdir / f"{path.stem}-{size[0]}x{size[1]}.jpg"
    if not out.exists():
        with Image.open(path) as im:
            im = ImageOps.exif_transpose(im).convert("RGB")
            im = ImageOps.fit(im, size, Image.LANCZOS, centering=(0.5, 0.45))
            im.save(out, "JPEG", quality=66, optimize=True)  # baseline: decodifica más rápido en celulares
    return out.name  # relativo a catalogo.html, que vive en la misma carpeta


# ---------------------------------------------------------------------------
# HTML de impresión
# ---------------------------------------------------------------------------

CSS = """
@page { size: A4; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  font-family: Arial, Helvetica, sans-serif;
  color: #2d2330;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}
:root {
  --bg: #fff8fb; --text: #2d2330; --muted: #736675;
  --primary: #e85d9e; --primary-dark: #b92f72; --violet: #7c5cff;
  --green: #1fae57; --green-dark: #128c45; --border: #f2d8e5;
}
.page {
  width: 210mm; height: 297mm;
  padding: 14mm 13mm 16mm;
  position: relative; overflow: hidden;
  page-break-after: always; break-after: page;
  background: var(--bg);
}
.page:last-child { page-break-after: auto; break-after: auto; }

/* ---- encabezado y pie de cada página ---- */
.page-head {
  display: flex; align-items: center; justify-content: space-between;
  padding-bottom: 3mm; margin-bottom: 5mm; border-bottom: 1.5px solid var(--border);
}
.page-head .brand { display: flex; align-items: center; gap: 3mm; }
.page-head img { width: 11mm; height: 11mm; object-fit: contain; }
.page-head strong { font-size: 11pt; display: block; }
.page-head small { color: var(--muted); font-size: 8pt; }
.page-head .tag {
  font-size: 8pt; font-weight: 700; color: var(--primary-dark);
  border: 1px solid var(--border); background: #fff;
  padding: 1.6mm 3.2mm; border-radius: 99px;
}
.page-foot {
  position: absolute; left: 13mm; right: 13mm; bottom: 7mm;
  display: flex; justify-content: space-between; align-items: center;
  font-size: 7.5pt; color: var(--muted);
}
.page-foot a { color: var(--green-dark); font-weight: 700; font-size: 9pt; text-decoration: none; }

/* ---- ícono de WhatsApp (SVG vectorial, liviano y nítido) ---- */
.wa { display: inline-flex; align-items: center; gap: 2mm; }
.wa-badge {
  width: 6mm; height: 6mm; border-radius: 50%; background: var(--green);
  display: inline-flex; align-items: center; justify-content: center; flex: none;
}
.wa-badge svg { width: 3.8mm; height: 3.8mm; display: block; fill: #fff; }

/* ---- portada ---- */
.cover { display: flex; flex-direction: column; text-align: center; }
.cover .logo { width: 34mm; height: 34mm; object-fit: contain; margin: 2mm auto 0; }
.cover .eyebrow {
  display: inline-block; margin: 5mm auto 0; padding: 2mm 5mm; border-radius: 99px;
  background: #fff; border: 1px solid var(--border);
  color: var(--primary-dark); font-weight: 700; font-size: 9.5pt;
}
.cover h1 {
  font-size: 30pt; line-height: 1.02; letter-spacing: -0.04em;
  margin: 5mm auto 3mm; max-width: 165mm;
}
.cover h1 em { font-style: normal; color: var(--primary); }
.cover .lead { color: var(--muted); font-size: 11pt; margin: 0 auto; max-width: 140mm; line-height: 1.45; }
.cover-collage {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 3mm;
  margin: 6mm 0 0;
}
.cover-collage img {
  width: 100%; aspect-ratio: 4 / 3; object-fit: cover; border-radius: 4mm;
  border: 1px solid var(--border); display: block;
}
.cover-index {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 3mm; margin: 6mm 0 6mm;
}
.cover-index div {
  background: #fff; border: 1px solid var(--border); border-top: 1.2mm solid var(--primary); border-radius: 4mm;
  padding: 3.2mm 2mm; font-size: 8.5pt; font-weight: 700;
}
.cover-contact {
  margin-top: auto; display: flex; align-items: center; justify-content: space-between; gap: 5mm;
  background: var(--primary-dark);
  color: #fff; border-radius: 6mm; padding: 6mm 7mm; text-align: left;
}
.cover-contact strong { font-size: 13pt; display: block; }
.cover-contact small { opacity: .9; font-size: 8.5pt; }
.cover-contact a {
  background: #fff; color: var(--primary-dark); font-weight: 700; text-decoration: none;
  padding: 2mm 5mm 2mm 2mm; border-radius: 99px; font-size: 10.5pt; white-space: nowrap;
}

/* ---- títulos de sección ---- */
.section-title { margin: 0 0 5mm; }
.section-title span {
  font-size: 8pt; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; color: var(--primary-dark);
}
.section-title h2 { font-size: 21pt; letter-spacing: -0.03em; margin: 1mm 0 0; }
.section-title p { margin: 1.5mm 0 0; color: var(--muted); font-size: 9pt; }
* + .section-title { margin-top: 7mm; }

/* ---- productos ---- */
.products { display: grid; grid-template-columns: repeat(3, 1fr); gap: 4mm; }
.products.cols-4 { grid-template-columns: repeat(4, 1fr); gap: 3mm; }
.products.cols-4 .pics > img { aspect-ratio: 4 / 3; }
.products.cols-4 .price { font-size: 11.5pt; }
.product {
  background: #fff; border: 1px solid var(--border); border-radius: 4.5mm;
  overflow: hidden; display: flex; flex-direction: column;
  break-inside: avoid;
}
.product .pics { position: relative; }
.product .pics > img { width: 100%; aspect-ratio: 16 / 10; object-fit: cover; display: block; }
.product .pill {
  position: absolute; left: 2mm; top: 2mm;
  background: rgba(255,255,255,.94); color: var(--primary-dark);
  font-size: 6.8pt; font-weight: 700; padding: .9mm 2.2mm; border-radius: 99px;
}
.product .body { padding: 3mm 3.2mm 3.4mm; display: flex; flex-direction: column; flex: 1; }
.product h3 { font-size: 9.6pt; margin: 0 0 1.2mm; line-height: 1.15; }
.product p { font-size: 7.6pt; color: var(--muted); margin: 0; line-height: 1.35; }
.product ul { margin: 1.4mm 0 0; padding-left: 3.6mm; font-size: 7.4pt; color: var(--muted); line-height: 1.35; }
.product .price {
  margin-top: auto; padding-top: 2.2mm;
  font-size: 12.5pt; font-weight: 700; color: var(--primary-dark);
}
.product .price small { font-size: 7.5pt; color: var(--muted); font-weight: 700; }
.product .tiers { display: flex; gap: 1.4mm; flex-wrap: wrap; margin-top: auto; padding-top: 2.2mm; }
.product .tiers span {
  font-size: 7.6pt; font-weight: 700; background: #fff3f8; color: var(--primary-dark);
  border: 1px solid var(--border); border-radius: 99px; padding: .9mm 2.2mm;
}

/* ---- servicios ---- */
.services { display: grid; grid-template-columns: repeat(3, 1fr); gap: 4mm; }
.service {
  background: #fff; border: 1px solid var(--border); border-radius: 4.5mm; overflow: hidden;
}
.service img { width: 100%; aspect-ratio: 5 / 2; object-fit: cover; display: block; }
.service div { padding: 3mm 3.2mm 3.4mm; }
.service h3 { font-size: 10pt; margin: 0 0 1mm; }
.service p { font-size: 7.6pt; color: var(--muted); margin: 0 0 2mm; line-height: 1.35; }
.service b { font-size: 8pt; color: var(--green); }

/* ---- combos ---- */
.combos { display: grid; grid-template-columns: 1fr 1fr; gap: 4mm; }
.combo {
  display: grid; grid-template-columns: 34mm 1fr; gap: 3.5mm; align-items: start;
  background: #fff; border: 1px solid var(--border); border-radius: 4.5mm; padding: 3mm;
}
.combo.featured { border: 1.5px solid var(--violet); }
.combo img { width: 34mm; height: 34mm; object-fit: cover; border-radius: 3mm; display: block; }
.combo .label { font-size: 7pt; font-weight: 700; text-transform: uppercase; letter-spacing: .06em; color: var(--violet); }
.combo h3 { font-size: 10.5pt; margin: .8mm 0 1.4mm; }
.combo ul { margin: 0; padding-left: 3.6mm; font-size: 7.6pt; color: var(--muted); line-height: 1.4; }
.combo b { display: block; margin-top: 1.8mm; font-size: 8pt; color: var(--green); }

/* ---- cómo pedir ---- */
.steps { display: grid; grid-template-columns: repeat(4, 1fr); gap: 3mm; }
.step { background: #fff; border: 1px solid var(--border); border-radius: 4.5mm; padding: 3.4mm; }
.step span {
  width: 7mm; height: 7mm; border-radius: 50%; display: grid; place-items: center;
  background: var(--primary); color: #fff;
  font-weight: 700; font-size: 9pt;
}
.step h3 { font-size: 9pt; margin: 2.2mm 0 1mm; }
.step p { font-size: 7.4pt; color: var(--muted); margin: 0; line-height: 1.35; }

.closing {
  margin-top: 8mm; text-align: center;
  background: var(--primary-dark);
  color: #fff; border-radius: 6mm; padding: 7mm 8mm;
}
.closing h2 { font-size: 17pt; margin: 0 0 2mm; letter-spacing: -0.02em; }
.closing p { margin: 0 auto 4mm; font-size: 9pt; max-width: 140mm; opacity: .95; line-height: 1.4; }
.closing a {
  background: #fff; color: var(--primary-dark); font-weight: 700;
  text-decoration: none; padding: 2mm 6mm 2mm 2mm; border-radius: 99px; font-size: 10.5pt;
}
.cover-contact .wa-badge, .closing .wa-badge { width: 7mm; height: 7mm; }
.cover-contact .wa-badge svg, .closing .wa-badge svg { width: 4.4mm; height: 4.4mm; }
.note { margin-top: 5mm; text-align: center; font-size: 7.5pt; color: var(--muted); }
"""


EMOJI = re.compile("[\U0001F000-\U0001FFFF\u2600-\u27BF\u2B00-\u2BFF\uFE0F\u200D]")


# Logo de WhatsApp (Simple Icons, CC0) como un único trazo vectorial.
WA_PATH = (
    "M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164"
    "-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297"
    "-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52"
    "-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074"
    "-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487"
    ".709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248"
    "-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214"
    "-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122"
    " 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815"
    " 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882"
    " 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"
)
WA_ICON = f'<span class="wa-badge"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="{WA_PATH}"/></svg></span>'


def esc(value):
    # Los emojis se incrustan como fuentes Type3 que hacen lento el PDF en celulares.
    return html.escape(EMOJI.sub("", value or "").strip(), quote=True)


def price_block(product):
    tiers = [item for item in product["items"] if re.match(r"^x\d+\s*:", item)]
    if tiers:
        chips = "".join(f"<span>{esc(t)}</span>" for t in tiers)
        return f'<div class="tiers">{chips}</div>'
    price = product["price"]
    if price.endswith(" c/u"):
        return f'<div class="price">{esc(price[:-4])} <small>c/u</small></div>'
    return f'<div class="price">{esc(price)}</div>'


def product_card(product, workdir, square=False):
    img = make_thumb(product["img"], workdir, (380, 285) if square else (440, 275))
    items = [i for i in product["items"]
             if not re.match(r"^x\d+\s*:", i) and not i.startswith("Ideal para")]
    items_html = f"<ul>{''.join(f'<li>{esc(i)}</li>' for i in items)}</ul>" if items else ""
    pill = f'<span class="pill">{esc(product["pill"])}</span>' if product["pill"] else ""
    return f"""
    <article class="product">
      <div class="pics">
        <img src="{img}" alt="{esc(product['name'])}">
        {pill}
      </div>
      <div class="body">
        <h3>{esc(product['name'])}</h3>
        <p>{esc(product['desc'])}</p>
        {items_html}
        {price_block(product)}
      </div>
    </article>"""


def page(content, tag, number, total, phone, wa_url, logo):
    return f"""
  <section class="page">
    <header class="page-head">
      <div class="brand">
        <img src="{logo}" alt="">
        <div><strong>Bar Papelería</strong><small>Papelería personalizada</small></div>
      </div>
      <span class="tag">{esc(tag)}</span>
    </header>
    {content}
    <footer class="page-foot">
      <a class="wa" href="{wa_url}">{WA_ICON}{esc(pretty_phone(phone))}</a>
      <span>Página {number} de {total}</span>
    </footer>
  </section>"""


def build_html(workdir):
    source = INDEX.read_text(encoding="utf-8")
    cumples = parse_products(source, "cumples")
    emprende = parse_products(source, "emprendimientos")
    services = parse_services(source)
    combos = parse_combos(source)
    steps = parse_steps(source)
    phone = parse_phone(source)
    wa_url = f"https://wa.me/{phone}"

    today = datetime.date.today()
    fecha = f"{MESES[today.month - 1].capitalize()} {today.year}"

    print(f"  {len(cumples)} productos de cumpleaños, {len(emprende)} de emprendimientos, "
          f"{len(services)} servicios, {len(combos)} combos")

    # Portada
    collage_src = [p["img"] for p in cumples[:3] + cumples[6:9]]
    collage = "".join(f'<img src="{make_thumb(s, workdir, (400, 300))}" alt="">' for s in collage_src)
    cover = f"""
  <section class="page cover">
    <img class="logo" src="{make_thumb('img/logo-bar.webp', workdir, (300, 300))}" alt="Bar Papelería">
    <span class="eyebrow">Catálogo con precios · {esc(fecha)}</span>
    <h1>Papelería personalizada para <em>cumpleaños, eventos y emprendimientos</em></h1>
    <p class="lead">Diseños personalizados, combos y detalles para que tu evento o emprendimiento se vea más lindo.</p>
    <div class="cover-collage">{collage}</div>
    <div class="cover-index">
      <div>Cumpleaños y eventos</div>
      <div>Emprendimientos</div>
      <div>Servicios rápidos</div>
      <div>Combos</div>
    </div>
    <div class="cover-contact">
      <div>
        <strong>Pedidos por WhatsApp</strong>
        <small>Provincia de Buenos Aires · Trabajos por encargo · Pedidos con seña</small>
      </div>
      <a class="wa" href="{wa_url}">{WA_ICON}{esc(pretty_phone(phone))}</a>
    </div>
  </section>"""

    def cards(products, cols4=False):
        cls = "products cols-4" if cols4 else "products"
        return f'<div class="{cls}">{"".join(product_card(p, workdir, cols4) for p in products)}</div>'

    cumple_page = f"""
    <div class="section-title"><span>Cumpleaños</span><h2>Cumpleaños y eventos</h2>
      <p>Personalizados con nombre, edad y temática. Pedí las unidades que necesites.</p></div>
    {cards(cumples, cols4=True)}"""

    services_html = "".join(f"""
      <article class="service">
        <img src="{make_thumb(s['img'], workdir, (440, 176))}" alt="">
        <div><h3>{esc(s['name'])}</h3><p>{esc(s['desc'])}</p><b>Consultar</b></div>
      </article>""" for s in services)

    combos_html = "".join(f"""
      <article class="combo{' featured' if i == 1 else ''}">
        <img src="{make_thumb(c['img'], workdir, (240, 240))}" alt="">
        <div>
          <span class="label">{esc(c['label'])}</span>
          <h3>{esc(c['name'])}</h3>
          <ul>{''.join(f'<li>{esc(it)}</li>' for it in c['items'])}</ul>
          <b>Consultar precio</b>
        </div>
      </article>""" for i, c in enumerate(combos))

    steps_html = "".join(f"""
      <article class="step"><span>{esc(s['num'])}</span><h3>{esc(s['name'])}</h3><p>{esc(s['desc'])}</p></article>"""
        for s in steps)

    emprende_page = f"""
    <div class="section-title"><span>Emprendimientos</span><h2>Para tu marca o negocio</h2>
      <p>Stickers, tarjetas y volantes personalizados.</p></div>
    {cards(emprende)}
    <div class="section-title"><span>Servicios rápidos</span><h2>Fotocopias, impresiones y anillados</h2></div>
    <div class="services">{services_html}</div>"""

    final_page = f"""
    <div class="section-title"><span>Lo más práctico</span><h2>Combos listos</h2>
      <p>Opciones pensadas para resolver pedidos frecuentes.</p></div>
    <div class="combos">{combos_html}</div>
    <div class="section-title"><span>Proceso de compra</span><h2>Cómo hacer un pedido</h2></div>
    <div class="steps">{steps_html}</div>
    <div class="closing">
      <h2>¿Ya elegiste qué necesitás?</h2>
      <p>Mandá producto, cantidad, temática y fecha del evento. Así cotizamos o confirmamos tu pedido más rápido.</p>
      <a class="wa" href="{wa_url}">{WA_ICON}Escribir por WhatsApp · {esc(pretty_phone(phone))}</a>
    </div>
    <p class="note">Precios actualizados a {esc(fecha)}. Pueden modificarse sin previo aviso; consultá disponibilidad, temática y fecha por WhatsApp.</p>"""

    inner = [
        ("Cumpleaños y eventos", cumple_page),
        ("Emprendimientos y servicios", emprende_page),
        ("Combos y pedidos", final_page),
    ]
    total = len(inner) + 1
    logo = make_thumb("img/logo-bar.webp", workdir, (120, 120))
    pages = [cover] + [page(content, tag, n + 2, total, phone, wa_url, logo)
                       for n, (tag, content) in enumerate(inner)]

    return f"""<!DOCTYPE html>
<html lang="es-AR">
<head>
<meta charset="UTF-8">
<title>Catálogo Bar Papelería</title>
<style>{CSS}</style>
</head>
<body>{''.join(pages)}
</body>
</html>"""


# ---------------------------------------------------------------------------
# Impresión
# ---------------------------------------------------------------------------

def find_browser():
    for candidate in BROWSERS:
        if os.path.isabs(candidate) and Path(candidate).exists():
            return candidate
        found = shutil.which(candidate)
        if found:
            return found
    sys.exit("No encontré Google Chrome ni Microsoft Edge para generar el PDF.")


def main():
    browser = find_browser()
    with tempfile.TemporaryDirectory(prefix="catalogo-pdf-") as tmp:
        workdir = Path(tmp)
        print("Leyendo index.html y preparando imágenes...")
        page_html = workdir / "catalogo.html"
        page_html.write_text(build_html(workdir), encoding="utf-8")

        # --html CARPETA: guarda también el HTML intermedio para revisarlo.
        if "--html" in sys.argv:
            keep = Path(sys.argv[sys.argv.index("--html") + 1]).resolve()
            shutil.rmtree(keep, ignore_errors=True)
            shutil.copytree(workdir, keep)
            print(f"HTML de vista previa en {keep / 'catalogo.html'}")

        print(f"Imprimiendo con {Path(browser).name}...")
        OUTPUT.parent.mkdir(exist_ok=True)
        subprocess.run([
            browser, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
            f"--user-data-dir={workdir / 'profile'}",
            "--allow-file-access-from-files",
            f"--print-to-pdf={OUTPUT}", page_html.as_uri(),
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)

    print(f"Listo: {OUTPUT.relative_to(ROOT)} ({OUTPUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
