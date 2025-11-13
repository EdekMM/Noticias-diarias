import os
import requests
from datetime import datetime, timezone, timedelta

# Configuración
API_KEY = os.getenv("NEWSAPI_KEY")
if not API_KEY:
    raise ValueError("Falta la variable de entorno NEWSAPI_KEY")

FUENTES = {
    "espana": "España",
    "madrid": "Madrid",
    "economia_mundial": "economía mundial",
    "economia_espana": "economía España",
    "construccion": "construcción",
    "acs_dragados": "ACS OR Dragados"
}

def obtener_noticias(query):
    url = f"https://newsapi.org/v2/everything?q={query}&language=es&sortBy=publishedAt&pageSize=3&apiKey={API_KEY}"
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()
    noticias = []
    for art in data.get("articles", []):
        noticias.append({
            "titulo": art["title"],
            "descripcion": art["description"] or "",
            "url": art["url"],
            "fuente": art["source"]["name"]
        })
    return noticias

def generar_feed(nombre, tema, noticias):
    madrid_tz = timezone(timedelta(hours=1))
    fecha = datetime.now(madrid_tz).strftime("%d/%m/%Y")
    pubdate = datetime.now(madrid_tz).strftime("%a, %d %b %Y %H:%M:%S +0100")

    xml_path = f"docs/{nombre}.xml.txt"
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write("<rss version='2.0'><channel>\n")
        f.write(f"<title>Noticias Diarias - {tema.title()}</title>\n")
        f.write(f"<link>https://edekmm.github.io/Noticias-diarias/docs/{nombre}.xml.txt</link>\n")
        f.write(f"<description>Noticias destacadas sobre {tema}.</description>\n")
        f.write("<language>es-es</language>\n")
        f.write("<item>\n")
        f.write(f"<title>Noticias del día {fecha}</title>\n")
        f.write("<description><![CDATA[\n")

        if noticias:
            for n in noticias:
                f.write(f"📰 <b>{n['titulo']}</b><br>")
                f.write(f"{n['descripcion']}<br>")
                f.write(f"<a href='{n['url']}'>{n['fuente']}</a><br><br>\n")
        else:
            f.write("No se encontraron noticias recientes.<br>\n")

        f.write("]]></description>\n")
        f.write(f"<pubDate>{pubdate}</pubDate>\n")
        f.write("</item></channel></rss>\n")
    print(f"✅ Feed generado: {xml_path}")

def main():
    os.makedirs("docs", exist_ok=True)
    for nombre, tema in FUENTES.items():
        try:
            noticias = obtener_noticias(tema)
            generar_feed(nombre, tema, noticias)
        except Exception as e:
            print(f"⚠️ Error al generar {nombre}: {e}")

if __name__ == "__main__":
    main()
