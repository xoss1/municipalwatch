# src/municipalwatch/scrapers/type_1.py
import re
import time
from bs4 import BeautifulSoup

def extract_type_0(session, item):
    """Extractor para plataformas del Tipo 1 (SEDELECTRONICA)"""
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-encoding": "gzip, deflate, br, zstd",
        "Connection": "keep-alive",
        "Host": item["host"],
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"
    }

    try:
        session.get(item["referer"], timeout=10)
        time.sleep(1)
        response = session.get(item["url"], headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        tbody = soup.find("tbody", id="id92")
        if not tbody:
            return None

        # Expresión regular para capturar los UUIDs de los edictos
        pattern = r'preview-document/([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'
        uuids = re.findall(pattern, str(tbody))

        if uuids:
            # Creamos una huella única basada en los UUIDs encontrados
            cadena_estado = "-".join(uuids)
            hash_estado = hashlib.md5(cadena_estado.encode("utf-8")).hexdigest()
            # Devolvemos el total de edictos y los primeros caracteres del hash como identificador
            return f"{len(uuids)}_{hash_estado[:8]}"

    except Exception as e:
        print(f"   ❌ Error en extractor tipo 1 [{item['nombre']}]: {e}")

    return None
