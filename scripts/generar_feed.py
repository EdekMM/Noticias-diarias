import datetime
import pytz
from pathlib import Path

# === Configuración ===
directorio = Path("docs")
directorio.mkdir(exist_ok=True)

zona_madrid = pytz.timezone("Europe/Madrid")
fecha = datetime.datetime.now(zona_madrid)
fecha_str = fecha.strftime("%d/%m/%Y")
pubdate = fecha.strftime("%a, %d %b %Y %H:%M:%S %z")

# === Definición de bloques ===
bloques = {
    "espana": {
        "titulo": "Noticias en España",
        "contenido": [
            "El Gobierno aprueba nuevas medidas económicas.",
            "La inflación se modera en el último trimestre.",
            "Se incrementa el empleo en el sector servicios."
        ],
        "resumen": "Resumen de las principales noticias nacionales del día."
    },
    "madrid": {
        "titulo": "Noticias en Madrid",
        "contenido": [
            "El Ayuntamiento presenta un nuevo plan de movilidad.",
            "Finalizan las obras en la M-30 antes de lo previsto.",
            "Aumenta la inversión en vivienda pública."
        ],
        "resumen": "Actualidad destacada de la Comunidad de Madrid."
    },
    "economia_mundial": {
        "titulo": "Economía Mundial",
        "contenido": [
            "El FMI revisa al alza el crecimiento global.",
            "El petróleo sube por tensiones geopolíticas.",
            "Wall Street cierra la jornada con leves subidas."
        ],
        "resumen": "Panorama económico internacional actualizado."
    },
    "economia_espana": {
        "titulo": "Economía en España",
        "contenido": [
            "El IBEX 35 supera los 10.000 puntos.",
            "Las exportaciones españolas alcanzan récord histórico.",
            "El sector industrial muestra señales de recuperación."
        ],
        "resumen": "Situación económica y financiera de España."
    },
    "construccion": {
        "titulo": "Sector de la Construcción",
        "contenido": [
            "Crecen las licitaciones públicas un 15% interanual.",
            "La demanda de vivienda nueva se mantiene estable.",
            "Avanza la digitalización de las constructoras."
        ],
        "resumen": "Noticias del sector inmobiliario y de infraestructuras."
    },
    "acs_dragados": {
        "titulo": "Grupo ACS / Dragados S.A.",
        "contenido": [
            "ACS anuncia nuevos contratos internacionales.",
            "Dragados lidera la construcción de un gran proyecto ferroviario.",
            "Florentino Pérez destaca la solidez financiera del grupo."
        ],
        "resumen": "Actualidad corporativa de ACS y sus filiales."
    }
}

# === Generar los archivos XML ===
for clave, datos in bloques.items():
    nombre_archivo = directorio / f"{clave}.xml.txt"
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write(f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>{datos['titulo']} - {fecha_str}</title>
    <link>https://edekmm.github.io/Noticias-diarias/docs/{clave}.xml.txt</link>
    <description>{datos['resumen']}</description>
    <language>es-es</language>

    <item>
      <title>{datos['titulo']} - {fecha_str}</title>
      <description><![CDATA[
      {"<br><br>".join([f"• {linea}" for linea in datos['contenido']])}
      ]]></description>
      <pubDate>{pubdate}</pubDate>
    </item>
  </channel>
</rss>""")

print("✅ Archivos XML generados correctamente.")
