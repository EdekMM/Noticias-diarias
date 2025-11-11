import feedparser, datetime, html

def obtener_titulares(fuentes, max_items=3):
    """Combina titulares y descripciones de varias fuentes RSS."""
    noticias = []
    for url in fuentes:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:max_items]:
                titulo = html.escape(entry.title)
                enlace = entry.link
                fuente = entry.link.split("/")[2]
                resumen = html.escape(entry.get("summary", ""))
                if len(resumen) > 250:  # Limitar longitud
                    resumen = resumen[:247] + "..."
                noticias.append(
                    f"- <a href='{enlace}'>{titulo}</a> ({fuente})"
                    f"<br><small>{resumen}</small>"
                )
        except Exception as e:
            noticias.append(f"- Error al obtener noticias de {url}: {e}")
    return "<br><br>".join(noticias) if noticias else "- Sin noticias disponibles"

bloques = {
    "🇪🇸 <b>Noticias en España:</b>": obtener_titulares([
        "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada",
        "https://e00-expansion.uecdn.es/rss/portada.xml",
        "https://www.abc.es/rss/feeds/abc_espana.xml",
    ]),
    "🏙️ <b>Noticias en Madrid:</b>": obtener_titulares([
        "https://www.20minutos.es/rss/madrid/",
        "https://www.telemadrid.es/rss.xml",
    ]),
    "🌍 <b>Economía mundial:</b>": obtener_titulares([
        "https://feeds.reuters.com/reuters/businessNews",
        "https://www.bbc.com/mundo/temas/economia/index.xml",
    ]),
    "💶 <b>Economía en España:</b>": obtener_titulares([
        "https://e00-expansion.uecdn.es/rss/economia.xml",
        "https://www.eleconomista.es/rss/rss-economia.php",
    ]),
    "🏗️ <b>Sector de la construcción:</b>": obtener_titulares([
        "https://www.construible.es/feed",
        "https://www.interempresas.net/Construccion/Articulos/feed",
    ]),
    "🏢 <b>Grupo ACS / Dragados S.A.:</b>": obtener_titulares([
        "https://e00-expansion.uecdn.es/rss/empresas.xml",
        "https://www.lainformacion.com/rss/empresas/",
    ]),
}

fecha_hoy = datetime.date.today().strftime("%d/%m/%Y")
pubdate = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0100")

with open("docs/noticias-diarias.xml.txt", "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<rss version="2.0">\n  <channel>\n')
    f.write('    <title>Noticias Diarias - España</title>\n')
    f.write('    <link>https://edekmm.github.io/Noticias-diarias/docs/noticias-diarias.xml.txt</link>\n')
    f.write('    <description>Noticias destacadas en España, Madrid, economía mundial, economía española, construcción y Grupo ACS / Dragados.</description>\n')
    f.write('    <language>es-es</language>\n\n')
    f.write(f'    <item>\n      <title>Noticias del día {fecha_hoy}</title>\n')
    f.write('      <description><![CDATA[\n')
    for bloque, contenido in bloques.items():
        f.write(f"{bloque}<br>{contenido}<br><br>\n")
    f.write('      ]]></description>\n')
    f.write(f'      <pubDate>{pubdate}</pubDate>\n')
    f.write('    </item>\n  </channel>\n</rss>')
