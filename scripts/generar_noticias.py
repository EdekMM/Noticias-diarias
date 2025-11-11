import feedparser
from datetime import datetime
import pytz
import html

# Fuentes RSS por categoría
FUENTES = {
    "España": [
        "https://www.elmundo.es/rss/espana.xml",
        "https://www.abc.es/rss/feeds/abc_Espana.xml",
        "https://www.elpais.com/rss/elpais/portada.xml"
    ],
    "Madrid": [
        "https://www.abc.es/rss/feeds/abc_Madrid.xml",
        "https://www.elmundo.es/rss/madrid.xml"
    ],
    "Economía mundial": [
        "https://www.ft.com/?format=rss",
        "https://feeds.reuters.com/reuters/businessNews"
    ],
    "Economía España": [
        "https://www.eleconomista.es/rss/rss-economia.php",
        "https://www.expansion.com/rss/economia.xml"
    ],
    "Construcción": [
        "https://www.construible.es/feed",
        "https://www.interempresas.net/Obra-Publica/Articulos.rss"
    ],
    "Grupo ACS / Dragados S.A.": [
        "https://www.europapress.es/rss/rss.aspx?ch=279"
    ]
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

def generar_feed():
    """Genera el RSS completo con un item por categoría."""
    zona_madrid = pytz.timezone("Europe/Madrid")
    ahora = datetime.now(zona_madrid)
    fecha = ahora.strftime("%d/%m/%Y")
    pubdate = ahora.strftime("%a, %d %b %Y %H:%M:%S %z")

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Noticias Diarias - España</title>
    <link>https://edekmm.github.io/Noticias-diarias/docs/noticias-diarias.xml</link>
    <description>Resumen diario con noticias destacadas en España, Madrid, economía mundial, economía española, construcción y Grupo ACS/Dragados.</description>
    <language>es-es</language>
"""

    for categoria, urls in FUENTES.items():
        items = obtener_titulares(urls)
        if not items:
            continue

        contenido = f"<h3>🗞️ <u>{categoria}</u></h3>\n<ul>\n"
        for titulo, resumen, link in items:
            contenido += f"<li><a href='{link}'><b>{titulo}</b></a><br>{resumen}</li><br>\n"
        contenido += "</ul>"

        rss += f"""
    <item>
      <title>{categoria} - Noticias del {fecha}</title>
      <description><![CDATA[{contenido}]]></description>
      <link>https://edekmm.github.io/Noticias-diarias/</link>
      <pubDate>{pubdate}</pubDate>
    </item>
"""

    rss += """
  </channel>
</rss>
"""

    with open("docs/noticias-diarias.xml", "w", encoding="utf-8") as f:
        f.write(rss)

if __name__ == "__main__":
    generar_feed()
