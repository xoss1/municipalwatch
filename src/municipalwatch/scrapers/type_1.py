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
        session.get(item["url"], timeout=10)
        time.sleep(1)
        response = session.get(item["url"], headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        
        tbody = soup.find("tbody", id="id92")
        if not tbody:
            return None

        expedientes_td = tbody.find_all("td", class_="class_folderCode")
        
        ids_encontrados = []
        for td in expedientes_td:
            texto = td.get_text(strip=True) # Ejemplos: "1604/2026", "1995/2024", "JGL/2026/11"
            
            # Buscamos patrones del tipo NÚMERO/AÑO (ej. 1604/2026)
            match_standard = re.search(r'(\d+)/(\d{4})', texto)
            # Buscamos patrones del tipo TEXTO/AÑO/NÚMERO (ej. JGL/2026/11)
            match_custom = re.search(r'/(\d{4})/(\d+)', texto)

            if match_standard:
                num, ano = match_standard.groups()
                # Formamos un ID ponderado por año: 202601604 (Año 2026 + número formateado)
                ids_encontrados.append(int(f"{ano}{int(num):05d}"))
            elif match_custom:
                ano, num = match_custom.groups()
                ids_encontrados.append(int(f"{ano}{int(num):05d}"))

        if ids_encontrados:
            return max(ids_encontrados)

    except Exception as e:
        print(f"   ❌ Error en extractor tipo 1 [{item['nombre']}]: {e}")

    return None
