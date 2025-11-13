#!/usr/bin/env python3
# scripts/generar_feeds.py
# Genera 6 feeds en docs/*.xml.txt usando NewsAPI y traducción (googletrans)
import os, requests, datetime, time
from googletrans import Translator

translator = Translator()
API_KEY = os.getenv("NEWSAPI_KEY", "")

# Definición de consultas (query) y emoji/icono por feed
FUENTES = {
    "espana": ("Spain", "🇪🇸"),
    "madrid": ("Madrid", "🏙️"),
    "economia_mundial": ("global economy", "🌍"),
    "economia_espana": ("Spain economy", "💶"),
    "construccion": ("construction sector Spain", "🏗️"),
    "acs_dragados": ("ACS OR Dragados", "🏢"),
}

def traducir(texto):
    if not texto:
        return ""
    try:
        return translator.translate(texto, dest="es").text
    except Exception:
        return texto

def obtener_noticias(query, page_size=3):
    if not API_KEY:
        return []
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": page_size,
        "apiKey": API_KEY
    }
    try:
        r = requests.get(url, params=params, timeout=15)
        data = r.json()
        articles = data.get("articles", []) if isinstance(data, dict) else []
    except Exception:
        articles = []
    noticias = []
    for art in articles:
        titulo_orig = art.get("title") or ""
        desc_orig = art.get("description") or ""
        link = art.get("url") or ""
        img = art.get("urlToImage") or ""
        # traducir (si falla, devuelve original)
        titulo = traducir(titulo_orig)
        desc = traducir(desc_orig)
        noticias.append((titulo, desc, link, img))
        # Sleep tiny to be polite with translator/network
        time.sleep(0.1)
    return noticias

def generar():
    docs_dir = "docs"
    os.makedirs(docs_dir, exist_ok=True)
    ahora = datetime.datetime.now()
    fecha = ahora.strftime("%d/%m/%Y")
    pubdate = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")

    for slug, (query, icono) in FUENTES.items():
        noticias = obtener_noticias(query, page_size=3)
        if not noticias:
            # Mensaje si no hay resultados
            noticias = [("Sin titulares disponibles", "No se han encontrado noticias para esta categoría.", "", "")]

        # Construir XML
        channel_title = f"Noticias diarias - {slug.replace('_',' ').title()}"
        link = f"https://edekmm.github.io/Noticias-diarias/docs/{slug}.xml.txt"
        xml_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<rss version="2.0">',
            '  <channel>',
            f'    <title>{channel_title}</title>',
            f'    <link>{link}</link>',
            f'    <description>Noticias sobre {query} actualizadas automáticamente.</description>',
            '    <language>es-es"',
            f'    <pubDate>{pubdate}</pubDate>'
        ]
        # Add items
        for t, d, l, img in noticias:
            img_html = f'<img src="{img}" width="120" style="border-radius:6px;"><br>' if img else ""
            description = f'{icono} {img_html}<b>{t}</b><br><br>{d}<br><a href="{l}">Leer más</a>'
            item = (
                "    <item>",
                f"      <title>{t}</title>",
                f"      <description><![CDATA[{description}]]></description>",
                f"      <link>{l}</link>",
                f"      <pubDate>{pubdate}</pubDate>",
                "    </item>",
            )
            xml_lines.extend(item)

        xml_lines.append("  </channel>")
        xml_lines.append("</rss>")

        contenido = "\n".join(xml_lines)
        ruta = os.path.join(docs_dir, f"{slug}.xml.txt")
        with open(ruta, "w", encoding="utf-8") as fh:
            fh.write(contenido)
        print(f"Generado: {ruta}")

if __name__ == "__main__":
    generar()
