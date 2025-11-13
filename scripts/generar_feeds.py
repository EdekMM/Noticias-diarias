import requests
import feedparser
from datetime import datetime
import html
import os

# -----------------------------
# CONFIG
# -----------------------------
API_KEY = d40030cf26d0445eb105613a3dfdbd2b  # ← tu API Key
MAX_TITULARES = 10

# Categorías y búsquedas
CATEGORIAS = {
    "espana": {
        "query": "España",
        "titulo": "Noticias de España"
    },
    "madrid": {
        "query": "Madrid",
        "titulo": "Noticias de Madrid"
    },
    "economia_mundial": {
        "query": "world economy",
        "titulo": "Economía mundial"
    },
    "economia_espana": {
        "query": "economía España",
        "titulo": "Economía en España"
    },
    "construccion": {
        "query": "sector construcción España",
        "titulo": "Sector de la construcción"
    },
    "acs_dragados": {
        "query": "ACS OR Dragados OR Florentino Pérez construcción",
        "titulo": "Grupo ACS / Dragados"
    }
}

# -----------------------------
# TRADUCTOR (mymemory)
# -----------------------------
def traducir(texto, origen="en"):
    if origen == "es":
        return texto

    url = "https://api.mymemory.translated.net/get"
    params = {"q": texto, "langpair": f"{origen}|es"}

    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        return data.get("responseData", {}).get("translatedText", texto)
    except:
        return texto


# -----------------------------
# FUENTE 1: NewsAPI
# -----------------------------
def obtener_newsapi(query):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "sortBy": "publishedAt",
        "language": "es",
        "pageSize": MAX_TITULARES,
        "apiKey": API_KEY
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        articulos = data.get("articles", [])
        return [a.get("title") for a in articulos if a.get("title")]
    except:
        return []


# -----------------------------
# FUENTE 2: Google News RSS
# -----------------------------
def obtener_google_news(query):
    url = f"https://news.google.com/rss/search?q={query}&hl=es&gl=ES&ceid=ES:es"
    feed = feedparser.parse(url)

    resultados = []
    for item in feed.entries[:MAX_TITULARES]:
        resultados.append(item.title)

    return resultados


# -----------------------------
# FUENTE 3: Reuters
# -----------------------------
def obtener_reuters():
    url = "https://feeds.reuters.com/reuters/worldNews"
    feed = feedparser.parse(url)
    resultados = []

    for item in feed.entries[:MAX_TITULARES]:
        resultados.append(traducir(item.title))

    return resultados


# -----------------------------
# FUENTE 4: BBC News
# -----------------------------
def obtener_bbc():
    url = "https://feeds.bbci.co.uk/news/world/rss.xml"
    feed = feedparser.parse(url)
    resultados = []

    for item in feed.entries[:MAX_TITULARES]:
        resultados.append(traducir(item.title))

    return resultados


# -----------------------------
# FUENTE 5: El País RSS
# -----------------------------
def obtener_el_pais():
    url = "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada"
    feed = feedparser.parse(url)
    resultados = []

    for item in feed.entries[:MAX_TITULARES]:
        resultados.append(item.title)

    return resultados


# -----------------------------
# UNIFICAR LAS FUENTES
# -----------------------------
def obtener_titulares(query):
    titulares = []

    # newsapi
    titulares.extend(obtener_newsapi(query))

    # google news
    titulares.extend(obtener_google_news(query))

    # fuentes internacionales
    titulares.extend(obtener_reuters())
    titulares.extend(obtener_bbc())

    # El País
    titulares.extend(obtener_el_pais())

    # eliminar duplicados y limitar
    titulos_unicos = []
    for t in titulares:
        if t not in titulos_unicos:
            titulos_unicos.append(t)

    return titulos_unicos[:MAX_TITULARES]


# -----------------------------
# CREAR XML DE FEED
# -----------------------------
def generar_xml(nombre, categoria, query):
    FECHA = datetime.now().strftime("%d/%m/%Y")
    PUBDATE = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0100")

    titulares = obtener_titulares(query)

    bloque = ""
    for i, t in enumerate(titulares, 1):
        bloque += f"{i}. {html.escape(t)}<br>\n"

    bloque += f"<br><b>Resumen automático generado el {FECHA}.</b>"

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>{categoria}</title>
    <link>https://edekmm.github.io/Noticias-diarias/docs/{nombre}.xml.txt</link>
    <description>{categoria}</description>
    <language>es-es</language>

    <item>
      <title>{categoria} - {FECHA}</title>
      <description><![CDATA[
{bloque}
]]></description>
      <pubDate>{PUBDATE}</pubDate>
    </item>
  </channel>
</rss>"""

    return xml


# -----------------------------
# GUARDAR ARCHIVOS
# -----------------------------
def main():
    os.makedirs("docs", exist_ok=True)

    for nombre, datos in CATEGORIAS.items():
        xml = generar_xml(nombre, datos["titulo"], datos["query"])
        ruta = f"docs/{nombre}.xml.txt"
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(xml)
        print(f"✔ Feed generado: {ruta}")


if __name__ == "__main__":
    main()
