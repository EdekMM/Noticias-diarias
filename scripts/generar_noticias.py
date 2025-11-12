import feedparser
from datetime import datetime
import pytz
import html
import os

# Fuentes RSS por categoría
FUENTES = {
    "espana": {
        "nombre": "España",
        "urls": [
            "https://www.elmundo.es/rss/espana.xml",
            "https://www.abc.es/rss/feeds/abc_Espana.xml",
            "https://www.elpais.com/rss/elpais/portada.xml"
        ],
    },
    "madrid": {
        "nombre": "Madrid",
        "urls": [
            "https://www.abc.es/rss/feeds/abc_Madrid.xml",
            "https://www.elmundo.es/rss/madrid.xml"
        ],
    },
    "economia-mundial": {
        "nombre": "Economía mundial",
        "urls": [
            "https://feeds.reuters.com/reuters/businessNews",
            "https://www.ft.com/?format=rss"
        ],
    },
    "economia-espana": {
        "nombre": "Economía España",
        "urls": [
            "https://www.eleconomista.es/rss/rss-economia.php",
            "https://www.expansion.com/rss/economia.xml"
        ],
    },
    "construccion": {
        "nombre": "Construcción",
        "urls": [
            "https://www.construible.es/feed",
            "https://www.interempresas.net/Obra-Publica/Articulos.rss"
        ],
    },
    "acs-dragados": {
        "nombre": "Grupo ACS / Dragados S.A.",
        "urls": [
            "https://www.europapress.es/rss/rss.aspx?ch=279"
        ],
    },
}


def obtener_titulares(urls, max_items=3):
    """Devuelve una lista de (título, resumen, enlace) desde varias fuentes."""
    items = []
    for url in urls:
        feed = feedparser.parse(url)
        for entry in feed.entries[:max_items]:
            titulo = html.escape(entry.title)
            link = entry.link
            resumen = html.escape(entry.get("summary", "")[:200].replace("\n", " "))
            items.append((titulo, resumen, link))
            if len(items) >= max_items:
                break
        if len(items) >= max_items:
            break
    return items


def generar_feed_individual(slug, nombre, urls):
    """Crea un feed RSS independiente para cada categoría."""
    zona_madrid = pytz.timezone("Europe/Madrid")
    ahora = datetime.now(zona_madrid)
    fecha = ahora.strftime("%d/%m/%Y")
    pubdate = ahora.strftime("%a, %d %b %Y %H:%M:%S %z")

    items = obtener_titulares(urls)
    if not items:
        print(f"⚠️  Sin noticias para {nombre}")
        return

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>{nombre} - Noticias Diarias</title>
    <link>https://edekmm.github.io/Noticias-diarias/docs/{slug}.xml</link>
    <description>Noticias destacadas de {nombre} actualizadas el {fecha}.</description>
    <language>es-es</language>
"""

    for titulo, resumen, link in items:
        rss += f"""
    <item>
      <title>{titulo}</title>
      <link>{link}</link>
      <description><![CDATA[{resumen}]]></description>
      <pubDate>{pubdate}</pubDate>
    </item>
"""

    rss += """
  </channel>
</rss>
"""

    os.makedirs("docs", exist_ok=True)
    ruta = f"docs/{slug}.xml"
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(rss)
    print(f"✅ Feed actualizado: {ruta}")


def generar_todos_los_feeds():
    for slug, datos in FUENTES.items():
        generar_feed_individual(slug, datos["nombre"], datos["urls"])


if __name__ == "__main__":
    generar_todos_los_feeds()
