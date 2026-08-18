# src/municipalwatch/scrapers/type_4.py (AYTO LORCA)
import re
import time
from bs4 import BeautifulSoup
from datetime import datetime

def extract_type_4(session, item):
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
        ids_encontrados = []
      
        for row in soup.select('#result_list tbody tr'):
          date_el = row.select_one('.publication_date')
          title_el = row.select_one('.title a')
          
          if date_el and title_el:
              date_text = date_el.get_text(strip=True)
              dt = datetime.strptime(date_text, "%d/%m/%Y %H:%M")
              ids_encontrados.append(int(dt.timestamp()))
            
              """
              entries.append({
                  'title': title_el.get_text(strip=True),
                  'publication_date': date_text,
                  'synthetic_id': int(dt.timestamp()) # A mayor fecha/hora, mayor número de ID
              })
              """
            if ids_encontrados:
                return max([int(i) for i in ids_encontrados])
    
    except Exception as e:
        print(f"   ❌ Error en extractor tipo 0 [{item['nombre']}]: {e}")

    return None
