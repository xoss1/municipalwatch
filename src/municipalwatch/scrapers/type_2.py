import re
import streamlit as st
import requests
from bs4 import BeautifulSoup

def extract_type_2(session, item):
    """
    Extractor para portales del tipo Sedipualba (Tipo 2).
    """
    url = item.get("url")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = session.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        html_content = response.text
    except Exception as e:
        print(f"Error al solicitar {url}: {e}")
        return False

    soup = BeautifulSoup(html_content, "html.parser")
    resultados = []
    max_id = 0

    # Buscamos la tabla con clase 'gridview'
    tabla = soup.find("table", class_="gridview")
    if not tabla:
        return False

    # Recorremos cada tbody dentro de la tabla
    tbodies = tabla.find_all("tbody")
    for tbody in tbodies:
        # 1. Obtener enlace e ID
        a_tag = tbody.find("a", href=re.compile(r"anuncio\.aspx\?id=\d+"))
        if not a_tag:
            continue
        
        href = a_tag.get("href", "")
        match_id = re.search(r"anuncio\.aspx\?id=(\d+)", href)
        if not match_id:
            continue
            
        anuncio_id = int(match_id.group(1))
        
        # Guardar el ID más alto encontrado para el historial
        if anuncio_id > max_id:
            max_id = anuncio_id

        # 2. Obtener fechas (publicación y retirada)
        fecha_pub = "N/A"
        fecha_ret = "N/A"
        # Buscamos el span con ID que contiene 'lblFecha'
        span_fecha = tbody.find("span", id=re.compile(r"lblFecha"))
        if span_fecha:
            texto_fecha = span_fecha.get_text(strip=True)
            # Separa por el guion entre las dos fechas
            partes_fecha = [f.strip() for f in texto_fecha.split("-")]
            if len(partes_fecha) >= 1:
                fecha_pub = partes_fecha[0]
            if len(partes_fecha) >= 2:
                fecha_ret = partes_fecha[1]

        # 3. Obtener Título (tercera celda <td>)
        tds = tbody.find_all("td")
        titulo = "N/A"
        if len(tds) >= 3:
            titulo = tds[2].get_text(strip=True)

        # Crear el bloque del edicto
        bloque = {
            "id": anuncio_id,
            "codigo_expediente": "N/A",
            "titulo": titulo,
            "fecha_publicacion": fecha_pub,
            "fecha_retirada": fecha_ret
        }
        
        resultados.append(bloque)

    if resultados:
        # Devuelve la lista de resultados y el ID máximo como requiere tu aplicación
        return [resultados, max_id]
    
    return False
