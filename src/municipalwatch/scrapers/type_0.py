# src/municipalwatch/scrapers/type_0.py
import re
import time
from bs4 import BeautifulSoup

def extract_type_0(session, item):
    """Extractor para plataformas de la Red de Sedes de la Región de Murcia (Tipo 0)."""
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-encoding": "gzip, deflate, br, zstd",
        "Connection": "keep-alive",
        "Host": item["host"],
        "Referer": item["referer"],
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/151.0.0.0 Safari/537.36"
    }

    try:
        session.get(item["referer"], timeout=10)
        time.sleep(1)
        response = session.get(item["url"], headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        script_tag = soup.find("script", string=re.compile(r"function\s+cargarLista"))

        if not script_tag:
            return None

        ids_encontrados = re.findall(r"listaJS\[j\]\s*=\s*\['(\d+)'", script_tag.string)
        if ids_encontrados:
            return max([int(i) for i in ids_encontrados])

    except Exception as e:
        print(f"   ❌ Error en extractor tipo 0 [{item['nombre']}]: {e}")

    return None
