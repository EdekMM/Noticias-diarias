#!/usr/bin/env python3
"""
scripts/generar-feeds.py

Genera 6 feeds (docs/*.xml.txt) tomando hasta MAX_TITULARES por categoría desde:
- NewsAPI (si NEWSAPI_KEY presente)
- Google News (RSS)
- Reuters RSS
- BBC RSS (Mundo)
- El País RSS
- GDELT (consulta artlist)
- Otros RSS españoles básicos

Traduce automáticamente titulares no-españoles usando MyMemory.
Diseñado para 'Amplia' + 'Español + traducidas'.
"""
import os
import requests
import feedparser
from datetime import datetime
from urllib.parse import quote
import html
import time

# -----------------------------
# CONFIGURACIÓN
# -----------------------------
NEWSAPI_KEY = os.getenv("d40030cf26d0445eb105613a3dfdbd2b", "")  # usa secret en GitHub Actions
MAX_TITULARES = 10
TIMEOUT = 12  # timeout de las peticiones

# Consultas amplias (RECOMENDADAS) para cada categoría
CATEGORIAS = {
    "espana": {
        "query": "España OR Spain OR economía España OR política España OR sucesos España",
        "titulo": "Noticias de España"
    },
    "madrid": {
        "query": "Madrid OR Comunidad de Madrid OR Ayuntamiento Madrid OR Alcaldía Madrid",
        "titulo": "Noticias de Madrid"
    },
    "economia_mundial": {
        "query": "global economy OR world economy OR international economy OR markets",
        "titulo": "Economía mundial"
    },
    "economia_espana": {
        "query": "economía España OR PIB España OR inflación España OR empleo España OR mercados España",
        "titulo": "Economía en España"
    },
    "construccion": {
        "query": "construcción OR obra pública OR vivienda OR inmobiliario OR sector construcción España",
        "titulo": "Sector de la construcción"
    },
    "acs_dragados": {
        "query": "ACS OR Dragados OR Grupo ACS OR Florentino Pérez OR contratos ACS",
        "titulo": "Grupo ACS / Dragados"
    }
}

# RSS extras (españolas y generales) - puedes ampliar esta lista si quieres
RSS_EXTRA = [
    # nacionales / economía
    "https://e00-elmundo.uecdn.es/elmundo/rss/portada.xml",
    "https://www.abc.es/rss/feeds/abcPortada.xml",
    "https://www.elconfidencial.com/rss/section/espana/",
    "https://www.elmundo.es/elmundo/rss/espana.xml",
    # internacionales
    "https://feeds.reuters.com/reuters/topNews",
    "https://feeds.bbci.co.uk/mundo/rss.xml",
    # sección economía El País (añadida también como fuente específica)
    "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/economia",
]

# -----------------------------
# UTIL: traducción simple con MyMemory
# -----------------------------
def traducir_mymemory(texto, src_lang="en"):
    """Traduce texto al español usando MyMemory (gratuito, con límites)."""
    if not texto:
        return ""
    try:
        # MyMemory langpair "en|es" — usamos src_lang por si detectamos diferente
        params = {"q": texto, "langpair": f"{src_lang}|es"}
        r = requests.get("https://api.mymemory.translated.net/get", params=params, timeout=TIMEOUT)
        data = r.json()
        return data.get("responseData", {}).get("translatedText", texto)
    except Exception:
        return texto

# -----------------------------
# OBTENER DE NEWSAPI
# -----------------------------
def obtener_newsapi(query, max_items=MAX_TITULARES):
    if not NEWSAPI_KEY:
        return []
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "sortBy": "publishedAt",
            "pageSize": max_items,
            # no forzamos language: queremos variedad; NewsAPI permite language param but we omit
            "apiKey": NEWSAPI_KEY
        }
        r = requests.get(url, params=params, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
        articles = data.get("articles", []) if isinstance(data, dict) else []
        results = []
        for art in articles[:max_items]:
            title = art.get("title") or ""
            # Some APIs include source language info, but not always; assume non-es needs translation
            # We'll detect naively: if title contains many ascii and no accented characters, translate later as fallback
            results.append({"titulo": title, "url": art.get("url", ""), "fuente": art.get("source", {}).get("name", "NewsAPI")})
        return results
    except Exception as e:
        print("⚠ ERROR NewsAPI:", e)
        return []

# -----------------------------
# OBTENER DE GOOGLE NEWS (RSS)
# -----------------------------
def obtener_google_news(query, max_items=MAX_TITULARES):
    try:
        qenc = quote(query)
        url = f"https://news.google.com/rss/search?q={qenc}&hl=es&gl=ES&ceid=ES:es"
        feed = feedparser.parse(url)
        results = []
        for entry in feed.entries[:max_items]:
            title = entry.get("title", "")
            link = entry.get("link", "")
            results.append({"titulo": title, "url": link, "fuente": "Google News"})
        return results
    except Exception as e:
        print("⚠ ERROR Google News:", e)
        return []

# -----------------------------
# OBTENER RSS genérico
# -----------------------------
def obtener_rss(url, max_items=MAX_TITULARES):
    try:
        feed = feedparser.parse(url)
        results = []
        for entry in feed.entries[:max_items]:
            title = entry.get("title", "")
            link = entry.get("link", "")
            results.append({"titulo": title, "url": link, "fuente": feed.feed.get("title", "RSS")})
        return results
    except Exception as e:
        print(f"⚠ ERROR RSS {url}: {e}")
        return []

# -----------------------------
# OBTENER GDELT (artlist)
# -----------------------------
def obtener_gdelt(query, max_items=MAX_TITULARES):
    try:
        # GDELT v2 doc API artlist mode
        qenc = quote(query)
        url = f"https://api.gdeltproject.org/api/v2/doc/doc?query={qenc}&mode=artlist&maxrecords={max_items}&format=json"
        r = requests.get(url, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
        results = []
        # GDELT returns 'articles' list with 'title' and 'url' sometimes under 'articles'
        articles = data.get("articles") or data.get("articles", []) or []
        # If structure different, try 'articles' fallback
        if not articles and isinstance(data.get("article"), dict):
            articles = [data.get("article")]
        for art in articles[:max_items]:
            title = art.get("title") or art.get("seendate") or ""
            link = art.get("url") or art.get("shareurl") or ""
            results.append({"titulo": title, "url": link, "fuente": "GDELT"})
        return results
    except Exception as e:
        print("⚠ ERROR GDELT:", e)
        return []

# -----------------------------
# RECOLECTAR y NORMALIZAR titulares
# -----------------------------
def recolectar_titulares(query, max_items=MAX_TITULARES):
    """Recolecta titulares de todas las fuentes y devuelve lista única de diccionarios."""
    collected = []

    # 1) NewsAPI (si hay key)
    try:
        na = obtener_newsapi(query, max_items)
        collected.extend(na)
    except Exception as e:
        print("Error al obtener NewsAPI:", e)

    # 2) Google News
    try:
        gn = obtener_google_news(query, max_items)
        collected.extend(gn)
    except Exception as e:
        print("Error Google News:", e)

    # 3) GDELT (potente fallback)
    try:
        gd = obtener_gdelt(query, max_items)
        collected.extend(gd)
    except Exception as e:
        print("Error GDELT:", e)

    # 4) RSS extras (Reuters, BBC, El País y otras)
    try:
        # Reuters top/world
        collected.extend(obtener_rss("https://feeds.reuters.com/reuters/topNews", max_items))
        # BBC Mundo or BBC World
        collected.extend(obtener_rss("https://feeds.bbci.co.uk/mundo/rss.xml", max_items))
        # El País (portada/economía)
        collected.extend(obtener_rss("https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/economia", max_items))
        # Otros RSS extras
        for rss in RSS_EXTRA:
            collected.extend(obtener_rss(rss, max_items))
    except Exception as e:
        print("Error en RSS extras:", e)

    # Normalizar: eliminar duplicados por título (manteniendo orden) y limitar a max_items
    seen = set()
    unique = []
    for item in collected:
        titulo_raw = (item.get("titulo") or "").strip()
        if not titulo_raw:
            continue
        # Normalize whitespace
        key = " ".join(titulo_raw.split()).lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
        if len(unique) >= max_items:
            break

    # Traducción: si el título parece no contener caracteres españoles comunes, intentar traducir
    for it in unique:
        titulo = it.get("titulo", "")
        # naive detect: si contiene letras acentuadas àâñáéíóúü or common spanish words, assume es-es
        has_spanish_chars = any(ch in titulo for ch in "áéíóúñü¿¡")
        if not has_spanish_chars:
            # traducir con MyMemory (src en 'en' por defecto; MyMemory detecta parcialmente)
            try:
                it["titulo"] = traducir_mymemory(titulo, src_lang="en")
                # small sleep to be polite with translator API
                time.sleep(0.1)
            except Exception:
                pass

    return unique[:max_items]

# -----------------------------
# GENERAR XML RSS para cada categoría
# -----------------------------
def generar_xml_para_categoria(slug, datos):
    query = datos["query"]
    titulo_channel = datos["titulo"]
    fecha = datetime.now().strftime("%d/%m/%Y")
    pubdate = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0100")

    print(f"\n--- Generando {slug} ({titulo_channel}) con query: {query}")

    items = recolectar_titulares(query, MAX_TITULARES)
    print(f"  -> Titulares recolectados: {len(items)}")

    # Si no hay items, añadimos un aviso
    if not items:
        items = [{"titulo": f"Sin titulares disponibles para {titulo_channel}", "url": "", "fuente": ""}]

    # Construir bloque HTML
    bloque = ""
    for i, it in enumerate(items, 1):
        fuente = it.get("fuente", "")
        titulo = it.get("titulo", "") or ""
        url = it.get("url", "") or ""
        # formato: "1. Título (Fuente) <br> Leer más: enlace"
        enlace_html = f' <a href="{url}">Leer más</a>' if url else ""
        bloque += f"{i}. <b>{html.escape(titulo)}</b> ({html.escape(str(fuente))}){enlace_html}<br>\n"

    bloque += f"<br><b>Resumen automático generado el {fecha}.</b>"

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>{titulo_channel}</title>
    <link>https://edekmm.github.io/Noticias-diarias/docs/{slug}.xml.txt</link>
    <description>{titulo_channel} — recopilación automática.</description>
    <language>es-es</language>

    <item>
      <title>{titulo_channel} - {fecha}</title>
      <description><![CDATA[
{bloque}
      ]]></description>
      <pubDate>{pubdate}</pubDate>
    </item>
  </channel>
</rss>
"""
    return xml

# -----------------------------
# MAIN
# -----------------------------
def main():
    if NEWSAPI_KEY:
        print("NewsAPI key encontrada: usando NewsAPI.")
    else:
        print("No se detectó NEWSAPI_KEY -> NewsAPI no se usará (se usarán las otras fuentes).")

    os.makedirs("docs", exist_ok=True)

    for slug, datos in CATEGORIAS.items():
        try:
            xml = generar_xml_para_categoria(slug, datos)
            ruta = f"docs/{slug}.xml.txt"
            with open(ruta, "w", encoding="utf-8") as fh:
                fh.write(xml)
            print(f"✔ Feed escrito: {ruta}")
        except Exception as e:
            print(f"⚠ ERROR generando {slug}: {e}")

if __name__ == "__main__":
    main()
