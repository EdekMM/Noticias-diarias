import os
from datetime import datetime

# Directorio de salida
output_dir = "docs"
os.makedirs(output_dir, exist_ok=True)

# Fecha actual
fecha = datetime.now().strftime("%d/%m/%Y")
pubdate = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0100")

# Bloques de noticias
feeds = {
    "espana": {
        "titulo": "Noticias de España",
        "descripcion": "Resumen de noticias nacionales de España.",
        "contenido": [
            "El Gobierno anuncia nuevas medidas económicas.",
            "El paro baja un 2% en el último trimestre.",
            "España refuerza su liderazgo en energías renovables."
        ]
    },
    "madrid": {
        "titulo": "Noticias de Madrid",
        "descripcion": "Actualidad de la Comunidad y ciudad de Madrid.",
        "contenido": [
            "El Ayuntamiento aprueba un nuevo plan de movilidad.",
            "Aumenta el turismo en la capital un 5% este mes.",
            "Nuevas obras en la M-30 para mejorar el tráfico."
        ]
    },
    "economia_mundial": {
        "titulo": "Economía Mundial",
        "descripcion": "Tendencias y titulares de la economía global.",
        "contenido": [
            "La FED mantiene los tipos de interés estables.",
            "El petróleo sube ligeramente por tensiones geopolíticas.",
            "China presenta datos de crecimiento mejores de lo esperado."
        ]
    },
    "economia_espana": {
        "titulo": "Economía en España",
        "descripcion": "Noticias sobre la economía y mercados españoles.",
        "contenido": [
            "El IBEX 35 cierra en positivo impulsado por la banca.",
            "El déficit público se reduce un 0.3% del PIB.",
            "El consumo interno muestra signos de recuperación."
        ]
    },
    "construccion": {
        "titulo": "Sector de la Construcción",
        "descripcion": "Noticias del sector inmobiliario y obras públicas.",
        "contenido": [
            "Las licitaciones de obra pública aumentan un 10%.",
            "El precio del cemento alcanza su nivel más alto desde 2018.",
            "Se anuncian nuevos proyectos de infraestructuras en Andalucía."
        ]
    },
    "acs_dragados": {
        "titulo": "Grupo ACS / Dragados S.A.",
        "descripcion": "Noticias corporativas del grupo ACS y sus filiales.",
        "contenido": [
            "ACS gana un contrato de 500 millones en Estados Unidos.",
            "Dragados participa en un nuevo túnel ferroviario en Alemania.",
            "El grupo presenta resultados trimestrales al alza."
        ]
    }
}

# Generar un XML por bloque
for clave, datos in feeds.items():
    file_path = os.path.join(output_dir, f"{clave}.xml.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>{datos['titulo']}</title>
    <link>https://edekmm.github.io/Noticias-diarias/docs/{clave}.xml.txt</link>
    <description>{datos['descripcion']}</description>
    <language>es-es</language>
    <pubDate>{pubdate}</pubDate>

""")
        for noticia in datos["contenido"]:
            f.write(f"""    <item>
      <title>{noticia}</title>
      <description><![CDATA[{noticia}]]></description>
      <pubDate>{pubdate}</pubDate>
    </item>
""")
        f.write("  </channel>\n</rss>")

print("Feeds generados correctamente.")
