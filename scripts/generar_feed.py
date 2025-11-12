import feedparser
from datetime import datetime
import pytz
import os

FEEDS = {
    "espana": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/espana/portada",
    "madrid": "https://www.telemadrid.es/rss",
    "economia_mundial": "https://www.reuters.com/rssFeed/businessNews",
    "economia_espana": "https://www.expansion.com/rss/economia.xml",
    "construccion": "https://www.construible.es/feed",
    "acs_dragados": "https://www.europapress.es/rss/rss.aspx?buscar=ACS+OR+Dragados"
}

OUTPUT_DIR = "docs"

os.makedirs(OUTPUT_DIR, exist_ok=True)

tz = pytz.timezone("Europe/Madrid")
fecha = datetime.now(tz).strftime("%d/%m/%Y")
pubdate = datetime.now(tz).strftime("%a, %d %b %Y %H:%M:%S %z")

def generar_feed(nombre, url):
    d = feedparser.parse(url)
    items = []
    for entry in d.entries[:3]:  # 3 titulares por bloque
        resumen = entry.get("summary", "")[:300].replace("\n", " ")
        items.append(f"""
        <item>
          <title>{entry.title}</title>
          <link>{entry.link}</link>
          <description><![CDATA[{resumen}]]></description>
          <pubDate>{pubdate}</pubDate>
        </item>
        """)
    contenido = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Noticias Diarias - {nombre.capitalize()}</title>
    <link>https://edekmm.github.io/Noticias-diarias/docs/{nombre}.xml.txt</link>
    <description>Noticias del bloque {nombre} generadas automáticamente.</description>
    <language>es-es</language>
    {''.join(items)}
  </channel>
</rss>"""
    with open(os.path.join(OUTPUT_DIR, f"{nombre}.xml.txt"), "w", encoding="utf-8") as f:
        f.write(contenido)
    print(f"✔ Feed generado: {nombre}.xml.txt")

for nombre, url in FEEDS.items():
    generar_feed(nombre, url)

print("✅ Todos los feeds generados correctamente.")

