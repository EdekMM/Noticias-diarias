import requests
import feedparser
from datetime import datetime
from urllib.parse import quote
import html
import os

# -----------------------------
# CONFIGURACIÓN
# -----------------------------
API_KEY = "PON_AQUI_TU_API_KEY"    # ← tu API Key
MAX_TITULARES = 10

CATEGORIAS = {
    "espana": {
        "query": "España NOT deportes NOT fútbol",
        "titulo": "Noticias de España"
    },
    "madrid": {
        "query": "Madrid NOT deportes NOT fútbol",
        "titulo": "Noticias de Madrid"
    },
    "economia_mundial": {
        "query": "world economy OR global economy",
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
# TRADUCTOR SIMPLE
# -----------------------------
def traducir(texto):
    url = "https://api.mymemory.translated.net/get"
    params = {"q": texto, "langpair": "en|es"}
    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        return data.get("responseData", {}).get("translatedText", texto)
    except:
        return texto


# -----------------------------
# NEWSAPI
# -----------------------------
def obtener_newsapi(query):
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "language": "es",
            "sortBy": "publishedAt",
            "pageSize": MAX_TITULARES,
            "apiKey": API_KEY
        }

        r = requests.get(url, params=params)
        data = r.json()
        articulos = data.get("articles", [])
        resultados = []

        for art in articulos[:MAX_TITULARES]:
            titulo = art.get("title", "Sin título")

            if art.get("language") != "es":
                titulo = traducir(titulo)

            resultados.append({
                "fuente": "NewsAPI",
                "titulo": titulo,
                "url": art.get("url", "")
            })

        return resultados

    except Exception as e:
        print("⚠ ERROR NewsAPI:", e)
        return []


# -----------------------------
# GOOGLE NEWS (CORREGIDO)
# -----------------------------
def obtener_google_news(query):
    try:
        query_encoded = quote(query)
        url = f"https://news.google.com/rss/search?q={query_encoded}&hl=es&gl=ES&ceid=ES:es"

        feed = feedparser.parse(url)
        resultados = []

        for item in feed.entries[:MAX_TITULARES]:
            resultados.append({
                "fuente": "Google News",
                "titulo": item.title,
                "url": item.link
            })

        return resultados

    except Exception as e:
        print("⚠ ERROR Google News:", e)
        return []


# -----------------------------
# RSS GENÉRICOS (Reuters, BBC, El País)
# -----------------------------
def obtener_rss(url):
    try:
        feed = feedparser.parse(url)
        resultados = []

        for item in feed.entries[:MAX_TITULARES]:
            titulo = item.title
            if "en" in feed.feed.get("language", "es"):
                titulo = traducir(titulo)

            resultados.append({
                "fuente": "RSS",
                "titulo": titulo,
                "url": item.link
            })

        return resultados
    except:
        return []


# -----------------------------
# OBTENER TITULARES (TODAS LAS FUENTES)
# -----------------------------
def obtener_titulares(query):

    titulares = []

    # 1) NewsAPI
    titulares.extend(obtener_newsapi(query))

    # 2) Google News
    titulares.extend(obtener_google_news(query))

    # 3) Reuters
    titulares.extend(obtener_rss("http://feeds.reuters.com/reuters/AF/worldNews"))

    # 4) BBC Mundo
    titulares.extend(obtener_rss("https://feeds.bbci.co.uk/mundo/rss.xml"))

    # 5) El País
    titulares.extend(obtener_rss("https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/sociedad"))

    # Limitar a MAX_TITULARES
    return titulares[:MAX_TITULARES]


# -----------------------------
# CREAR XML PARA CADA CATEGORÍA
# -----------------------------
def generar_xml(nombre, categoria, query):
    FECHA = datetime.now().strftime("%d/%m/%Y")
    PUBDATE = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0100")

    titulares = obtener_titulares(query)

    bloque = ""
    for t in titulares:
        bloque += f"- <b>{html.escape(t['titulo'])}</b> ({t['fuente']})<br>\n"

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
</rss>
"""
    return xml


# -----------------------------
# GUARDAR TODOS LOS FEEDS
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
