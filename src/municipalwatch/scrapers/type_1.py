import re
from bs4 import BeautifulSoup

def extract_type_1(session, item):
    """
    Extractor para plataformas del Tipo 1 (SEDELECTRONICA / Gestiona).
    Cuenta el número total de edictos presentes en la tabla.
    """
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Connection": "keep-alive",
        "Host": item["host"],
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"
    }

    try:
        response = session.get(item["url"], headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Localizar el cuerpo de la tabla por ID
        tbody = soup.find("tbody", id="id92")
        if not tbody:
            return None

        # Opción 1: Contar los enlaces a documentos mediante la expresión regular de UUIDs
        pattern = r'preview-document/[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}'
        uuids = re.findall(pattern, str(tbody))

        if uuids:
            # Devolvemos un NÚMERO ENTERO con el total de edictos encontrados
            return int(len(uuids))

        # Opción 2 (Fallback): Contar directamente las filas <tr> que contengan expediente
        filas = tbody.find_all("tr")
        total_edictos = 0
        for fila in filas:
            if fila.find("td", class_="class_folderCode"):
                total_edictos += 1

        return int(total_edictos) if total_edictos > 0 else 0

    except Exception as e:
        print(f"   ❌ Error en extractor tipo 1 [{item['nombre']}]: {e}")

    return None
