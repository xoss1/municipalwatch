import re
import requests
import streamlit as st

def extract_type_1(session, item):
    """Extractor para plataformas Tipo 1 con depuración en tiempo real."""
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive",
        "Host": item.get("host", ""),
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        url_base = item["url"]
        #st.write(f"🔍 **[DEBUG] Escaneando {item['nombre']}:** `{url}`")
        session = requests.Session()
        response = session.get(url_base, headers=headers, timeout=15, allow_redirects=True)
        #st.write(f"👉 **[DEBUG] Código HTTP respuesta:** `{response.status_code}`")

        if response.status_code != 200:
            #st.error(f"❌ La web devolvió un estado no válido: {response.status_code}")
            return None

        html_text = response.text
        #st.write(f"📄 **[DEBUG] Longitud del HTML recibido:** `{len(html_text)}` caracteres")

        patron = r"wicketAjaxGet\('\?(x=[^']+)'"

        # Guardamos la página inicial en la variable acumulada
        html_acumulado = html_text
        
        for i in range(0, 5):
          print(i)
        
          # 1. Buscamos el botón en el HTML de la iteración actual
          resultado = re.findall(patron, html_text, re.DOTALL)
        
          # 2. Control de seguridad: si no hay más botones, salimos del bucle
          if not resultado:
              print(f"No se encontró el botón 'Mostrar más' en la iteración {i}. Fin del proceso.")
              break
        
          # Tomamos el parámetro (o resultado[-1] si hubiera más de uno en el fragmento)
          parametro = resultado[0]
          url = url_base + parametro
        
          # 3. Hacemos la petición
          response_page = session.get(url, headers=headers, timeout=15, allow_redirects=True)
        
          # 4. Actualizamos html_text SOLO con la respuesta nueva para la siguiente búsqueda
          html_text = response_page.text
        
          # 5. Acumulamos el nuevo fragmento en el texto final
          html_acumulado += response_page.text
        
          # Al terminar el bucle, 'html_acumulado' contendrá la página inicial + las 5 respuestas         
        
        # Buscar apariciones de preview-document
        uuids = re.findall(r'preview-document/([a-f0-9-]+)', html_text)
        #st.write(f"📎 **[DEBUG] Documentos 'preview-document' hallados:** `{len(uuids)}`")

        ids_encontrados = []
        resultados = []
        # 1. Estrategia primaria: Extraer filas (<tr>) para vincular Fecha de Publicación + Nº Expediente
        filas = re.findall(r'<tr[^>]*>(.*?)</tr>', html_acumulado, re.DOTALL)
        for fila in filas:
            match_exp = re.search(r'class_folderCode[^>]*>.*?<span>([^<]+)</span>', fila, re.DOTALL)
            match_fecha = re.search(r'class_dateFrom[^>]*>.*?<span>([^<]+)</span>', fila, re.DOTALL)
            match_titulo = re.search(r'class_description[^>]*>.*?<span>([^<]+)</span>', fila, re.DOTALL)

            if match_exp and match_fecha:
                txt_exp = match_exp.group(1).strip()
                txt_fecha = match_fecha.group(1).strip()
                txt_titulo = match_titulo.group(1).strip() if match_titulo else "-"

                # Extraer Fecha (DD/MM/AAAA -> AAAAMMDD)
                m_fecha = re.search(r'(\d{2})/(\d{2})/(\d{4})', txt_fecha)
                # Extraer primer bloque numérico del expediente
                m_num = re.search(r'(\d+)', txt_exp)

                if m_fecha:
                    dia, mes, ano = m_fecha.groups()
                    fecha_int = int(f"{ano}{mes}{dia}")
                    num_exp = int(m_num.group(1)) if m_num else 0
                    
                    # ID único numérico
                    bloque_id = int(f"{fecha_int}{num_exp:05d}")
                    ids_encontrados.append(bloque_id)

                    # Estructuración del bloque según requerimiento
                    bloque = {
                        "id": bloque_id,
                        "titulo": txt_titulo,
                        "fecha_publicacion": txt_fecha,
                        "fecha_retirada": "-",
                        "codigo_expediente": txt_exp
                    }
                    resultados.append(bloque)

        # Retornar tuple de [resultados, max_id]
        if ids_encontrados:
            return [resultados, max(ids_encontrados)]
        else:
            pass

    except Exception as e:
        #st.error(f"💥 **[DEBUG] Excepción capturada en {item['nombre']}:** `{e}`")
        pass

    return None
