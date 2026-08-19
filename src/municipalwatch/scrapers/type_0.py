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
        # Patrón que localiza cada encabezado 'listaJS[...' y extrae exactamente los 5 campos requeridos
        patron = re.compile(
          r"listaJS\[[^\]]+\]\s*=\s*\[\s*'([^']*)'"                           # ID (Elemento 0)
          r"[\s\S]*?\/\/\s*3\s*'([^']*)'"                                      # Título (Trae el elemento tras //3 -> Índice 4)
          r"[\s\S]*?\/\/\s*5\s*'(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2})'"            # Fecha Pub (Trae tras //5 -> Índice 6)
          r"[\s\S]*?\/\/\s*6\s*'(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2})'"            # Fecha Ret (Trae tras //6 -> Índice 7)
          r"[\s\S]*?\/\/\s*10\s*'([^'\\]*(?:\\\/[^']*)*)'",
          re.DOTALL
        )
    
        resultados = []
    
        for match in patron.finditer(response.text):
          # Decodificamos secuencias Unicode como '\u00F3' a caracteres reales ('ó')
          titulo_raw = match.group(2)
          titulo_clean = bytes(titulo_raw, 'utf-8').decode('unicode-escape')
          
          # Limpiamos los escapes de barra '\/' del expediente
          expediente_clean = match.group(5).replace(r'\/', '/')
          
          bloque = {
              "id": match.group(1),
              "titulo": titulo_clean,
              "fecha_publicacion": match.group(3),
              "fecha_retirada": match.group(4),
              "codigo_expediente": expediente_clean
          }
          resultados.append(bloque)
        if ids_encontrados:
          return [resultados, max([int(i) for i in ids_encontrados])]

    except Exception as e:
        print(f"   ❌ Error en extractor tipo 0 [{item['nombre']}]: {e}")

    return None
