# src/municipalwatch/scrapers/type_1.py
import re
from bs4 import BeautifulSoup

def extract_type_1(session, item):
    """Extractor para plataformas del Tipo 1 (SEDELECTRONICA / Gestiona)."""
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive",
        "Host": item["host"],
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/151.0.0.0 Safari/537.36"
    }

    try:
        response = session.get(item["url"], headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        
        tbody = soup.find("tbody", id="id92")
        if not tbody:
            return None

        # 1. Buscamos todas las celdas de expediente en la tabla
        expedientes_td = tbody.find_all("td", class_="class_folderCode")
        
        ids_encontrados = []
        for td in expedientes_td:
            texto = td.get_text(strip=True) # Ejemplos: "1604/2026", "1995/2024", "JGL/2026/11"
            # 2. Extraemos los dígitos del número de expediente
            match = re.search(r'(\d+)', texto)
            if match:
                ids_encontrados.append(int(match.group(1)))

        # 3. Misma lógica del Tipo 0: devolver el mayor de la lista
        if ids_encontrados:
            return max(ids_encontrados)

    except Exception as e:
        print(f"   ❌ Error en extractor tipo 1 [{item['nombre']}]: {e}")

    return None
