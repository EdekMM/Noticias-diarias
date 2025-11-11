import feedparser
from datetime import datetime
import pytz
import html

# 🔹 Categorías y sus fuentes RSS en Google News
CATEGORIES = {
    "España": "https://news.google.com/rss?hl=es&gl=ES&ceid=ES:es",
    "Madrid": "https://news.google.com/rss/search?q=Madrid&hl=es&gl=ES&ceid=ES:es",
    "Economía Mundial": "https://news.google.com/rss/search?q=econom%C3%ADa+mundial&hl=es&gl=ES&ceid=ES:es",
    "Economía España": "https://news.google.com/rss/search?q=econom%C3%ADa+Espa%C3%B1a&hl=es&gl=ES&ceid=ES:es",
    "Construcción": "https://news.google.com/rss/search?q=sector+construcci%C3%B3n&hl=es&gl=ES&ceid=ES:es",
    "Grupo ACS / Dragados": "https://news.google.com/rss/search?q=grupo+ACS+OR+Dragados&hl=es&gl=ES&ceid=ES:es"
}

# 🕒 Fecha y hora local de Madrid
tz = pytz.timezone("Europe/Madrid")
fecha_hoy = datetime.now(tz)
fecha_str = fecha_hoy.strftime("%d/%m/%Y")
pub_date = fecha_hoy.strftime("%a, %d %b %Y %H:%M:%S %z")

# 🧩 Cabecera XML RSS
rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Noticias Diarias - España</title>
    <link>https://edekmm.github.io/Noticias-diarias/docs/noticias-diarias.xml</link>
    <description>Noticias destacadas en España, Madrid, economía mundial, economía española, construcción y Grupo ACS / Dragados.</description>
    <language>es-es</language>
    <item>
      <title>🗓️ Noticias del día {fecha_str}</title>
      <description><![CDATA[
"""

# 🔹 Recorrer categorías y añadir noticias numeradas
for categoria, url in CATEGORIES.items():
    feed = feedparser.parse(url)
    rss += f"<h3>🗞️ <u>{categoria}</u></h3>\n<ul>\n"

    if not feed.entries:
        rss += f"<li>No se han encontrado noticias recientes para {categoria}.</li>\n"
    else:
        for i, entry in enumerate(feed.entries[:3], start=1):
            num = ["1️⃣", "2️⃣", "3️⃣"][i-1] if i <= 3 else f"{i}."
            titulo = html.escape(entry.title)
            link = entry.link
            resumen = html.escape(entry.get('summary', '')[:250]).replace('\n', ' ').strip()
            rss += f"<li>{num} <a href='{link}'><b>{titulo}</b></a><br>{resumen}</li><br>\n"

    rss += "</ul>\n<hr style='border:0;border-top:1px solid #ccc;margin:15px 0;'>\n"

# 🔚 Cierre del XML
rss += f"""]]></description>
      <pubDate>{pub_date}</pubDate>
    </item>
  </channel>
</rss>"""

# 💾 Guardar el archivo RSS en /docs/
with open("docs/noticias-diarias.xml", "w", encoding="utf-8") as f:
    f.write(rss)

print("✅ Feed actualizado correctamente con titulares numerados.")
