import requests
from datetime import datetime
import html
import os

# -----------------------------
# CONFIGURACIÓN
# -----------------------------
API_KEY = "AQUI_TU_API_KEY_DE_NEWSAPI"   # ← pon aquí tu API Key
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
        "query": "global economy OR world economy",
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
# TRADUCTOR SIMPLE (Google-free)
# -----------------------------
def traducir(texto):
    url = "https://api.mymemory.translated.net/get"
    params = {"q": texto, "langpair": "en|es"}
    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        return data.get("responseData", {}).get("translatedText", texto)
    except:
        return texto  # Si falla, devuelve el original


# -----------------------------
# OBTENER TITULARES
# -----------------------------
def obtener_titulares(query):
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

    titulares = []
    for art in articulos[:MAX_TITULARES]:
        titulo = art.get("title", "Sin título")

        # Traducir si viene de fuente internacional
        if art.get("language", "es") != "es":
            titulo = traducir(titulo)

        titulares.append(titulo)

    return titulares


# -----------------------------
# CREAR XML
# -----------------------------
def generar_xml(nombre, categoria, query):
    FECHA = datetime.now().strftime("%d/%m/%Y")
    PUBDATE = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0100")

    # Obtener titulares
    titulares = obtener_titulares(query)

    # Armar bloque HTML
    bloque = ""
    for i, t in enumerate(titulares, 1):
        bloque += f"- {html.escape(t)}<br>\n"

    # Resumen final genérico
    resumen = f"Resumen automático generado el {FECHA}."

    bloque += f"<br><b>{resumen}</b>"

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
