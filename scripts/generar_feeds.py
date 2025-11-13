#!/usr/bin/env python3
# scripts/generar_feeds.py
import os
import requests
import datetime
import time
from googletrans import Translator

translator = Translator()
API_KEY = os.getenv("NEWSAPI_KEY", "")

# Categorías: (queries preferidas, fallback queries)
FUENTES = {
    "espana": (["Spain", "España", "España NOT Covid"], ["Spain"]),
    "madrid": (["Madrid", "Madrid España"], ["Madrid Spain", "Comunidad de Madrid"]),
    "economia_mundial": (["global economy", "economy"], ["world economy", "economía mundial"]),
    "economia_espana": (["Spain economy", "economía España"], ["economía España", "economia españa"]),
    "construccion": (["construction Spain", "sector construcción"], ["construction", "building sector"]),
    "acs_dragados": (["ACS OR Dragados", "ACS company"], ["ACS", "Dragados"])
}

HEADERS = {"User-Agent": "Noticias-Diarias-bot/1.0"}

def traducir(texto):
    if not texto:
        return ""
    try:
        return translator.translate(texto, dest="es").text
    except Exception:
        return texto

def newsapi_query(q, language="es", page_size=3):
    if not API_KEY:
        return []
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": q,
        "language": language,
        "sortBy": "publishedAt",
        "pageSize": page_size,
        "apiKey": API_KEY
    }
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=15)
        r.raise_for_status()
        data = r.json()
        articles = data.get("articles", []) if isinstance(data, dict) else []
        return articles
    except Exception as e:
        print(f"⚠️ Error consulta NewsAPI q='{q}' lang={language}: {e}")
        return []

def obtener_noticias_para_fuente(queries):
    # Intenta con language=es, si no hay resultados intenta english y queries alternativos
    resultados = []
    for q in queries:
        # 1) intentar en español
        arts = newsapi_query(q, language="es", page_size=3)
        if arts:
            return arts
        # 2) intentar en inglés (muchas fuentes devuelven artículos en inglés)
        arts = newsapi_query(q, language="en", page_size=3)
        if arts:
            return arts
        # 3) si no, prueba la siguiente query del listado
    # si todo falla, intenta ampliar con query genérica en inglés
    generic = newsapi_query("news " + " ".join(queries), language="en", page_size=3)
    return generic

def build_xml_items(articles, icono):
    items = []
    for art in articles:
        title_orig = art.get("title") or ""
        desc_orig = art.get("description") or ""
        url = art.get("url") or ""
        url_img = art.get("urlToImage") or ""
        # traducir al español si la entrada está en otro idioma
        title = traducir(title_orig) if title_orig else "Sin título"
        desc = traducir(desc_orig) if desc_orig else ""
        img_html = f'<img src="{url_img}" width="120" style="border-radius:6px;"><br>' if url_img else ""
        description = f'{icono} {img_html}<b>{title}</b><br><br>{desc}<br><a href="{url}">Leer más</a>'
        item = {
            "title": title,
            "description": description,
            "link": url,
        }
        items.append(item)
    return items

def generar():
    docs_dir = "docs"
    os.makedirs(docs_dir, exist_ok=True)
    ahora = datetime.datetime.now()
    fecha = ahora.strftime("%d/%m/%Y")
    pubdate = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")

    for slug, (preferred_queries, fallback) in FUENTES.items():
        print(f"\n=== Procesando {slug} ===")
        # combinar listas (preferred primero)
        queries_to_try = preferred_queries + (fallback if isinstance(fallback, list) else [])
        articles = obtener_noticias_para_fuente(queries_to_try)
        print(f"  Encontrados {len(articles)} artículos para {slug} con queries: {queries_to_try[:3]}")
        # si no hay artículos, escribimos un item de aviso
        if not articles:
            items = [{
                "title": f"Sin titulares disponibles para {slug}",
                "description": f"No se han encontrado noticias para la categoría {slug} hoy.",
                "link": ""
            }]
        else:
            built = build_xml_items(articles, icono_for_slug(slug))
            items = built

        # crear XML
        channel_title = f"Noticias diarias - {slug.replace('_',' ').title()}"
        link = f"https://edekmm.github.io/Noticias-diarias/docs/{slug}.xml.txt"
        xml_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<rss version="2.0">',
            '  <channel>',
            f'    <title>{channel_title}</title>',
            f'    <link>{link}</link>',
            f'    <description>Noticias sobre {slug} actualizadas automáticamente ({fecha}).</description>',
            '    <language>es-es"',
            f'    <pubDate>{pubdate}</pubDate>'
        ]
        for it in items:
            xml_lines.extend([
                '    <item>',
                f'      <title>{escape_xml(it["title"])}</title>',
                f'      <description><![CDATA[{it["description"]}]]></description>',
                f'      <link>{it["link"]}</link>',
                f'      <pubDate>{pubdate}</pubDate>',
                '    </item>',
            ])
        xml_lines.append('  </channel>')
        xml_lines.append('</rss>')

        contenido = "\n".join(xml_lines)
        ruta = os.path.join(docs_dir, f"{slug}.xml.txt")
        with open(ruta, "w", encoding="utf-8") as fh:
            fh.write(contenido)
        print(f"✅ Generado {ruta} ({len(items)} items)")

def escape_xml(text):
    # mínimo escape para títulos
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;"))

def icono_for_slug(slug):
    mapping = {
        "espana": "🇪🇸",
        "madrid": "🏙️",
        "economia_mundial": "🌍",
        "economia_espana": "💶",
        "construccion": "🏗️",
        "acs_dragados": "🏢"
    }
    return mapping.get(slug, "")

if __name__ == "__main__":
    generar()
