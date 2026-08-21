import re
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
        url = item["url"]
        #st.write(f"🔍 **[DEBUG] Escaneando {item['nombre']}:** `{url}`")
        
        response = session.get(url, headers=headers, timeout=15, allow_redirects=True)
        #st.write(f"👉 **[DEBUG] Código HTTP respuesta:** `{response.status_code}`")

        if response.status_code != 200:
            #st.error(f"❌ La web devolvió un estado no válido: {response.status_code}")
            return None

        html_text = response.text
        #st.write(f"📄 **[DEBUG] Longitud del HTML recibido:** `{len(html_text)}` caracteres")

        # Comprobar si id92 está presente en la respuesta
        tiene_id92 = "id92" in html_text
        #st.write(f"🧩 **[DEBUG] ¿Contiene 'id92' el HTML?:** `{tiene_id92}`")

        # Buscar apariciones de preview-document
        uuids = re.findall(r'preview-document/([a-f0-9-]+)', html_text)
        #st.write(f"📎 **[DEBUG] Documentos 'preview-document' hallados:** `{len(uuids)}`")

        ids_encontrados = []

        # 1. Estrategia primaria: Extraer filas (<tr>) para vincular Fecha de Publicación + Nº Expediente
        filas = re.findall(r'<tr[^>]*>(.*?)</tr>', html_text, re.DOTALL)
        for fila in filas:
            match_exp = re.search(r'class_folderCode[^>]*>.*?<span>([^<]+)</span>', fila, re.DOTALL)
            match_fecha = re.search(r'class_dateFrom[^>]*>.*?<span>([^<]+)</span>', fila, re.DOTALL)

            if match_exp and match_fecha:
                txt_exp = match_exp.group(1).strip()
                txt_fecha = match_fecha.group(1).strip()

                # Extraer Fecha (DD/MM/AAAA -> AAAAMMDD)
                m_fecha = re.search(r'(\d{2})/(\d{2})/(\d{4})', txt_fecha)
                # Extraer primer bloque numérico del expediente
                m_num = re.search(r'(\d+)', txt_exp)

                if m_fecha:
                    dia, mes, ano = m_fecha.groups()
                    fecha_int = int(f"{ano}{mes}{dia}")
                    num_exp = int(m_num.group(1)) if m_num else 0
                    
                    # ID Incremental: AAAAMMDD + Nº Expediente a 5 dígitos (Ej: 2026080401995)
                    ids_encontrados.append(int(f"{fecha_int}{num_exp:05d}"))

        #st.write(f"📑 **[DEBUG] IDs Fecha+Expediente generados:** `{ids_encontrados[:3]}`...")

        # 2. Plan B: Si la tabla cambia de estructura, usará los UUIDs como respaldo
        if not ids_encontrados and uuids:
            #st.write("⚠️ **[DEBUG] Fallback a conteo por UUIDs**")
            ids_encontrados.append(len(set(uuids)))

        if ids_encontrados:
            id_maximo = max(ids_encontrados)
            #st.success(f"✅ **[DEBUG] ID Máximo calculated para {item['nombre']}:** `{id_maximo}`")
            return id_maximo
        else:
            #st.warning(f"⚠️ **[DEBUG] No se pudo calcular ningún ID numérico para {item['nombre']}.**")
            pass

    except Exception as e:
        #st.error(f"💥 **[DEBUG] Excepción capturada en {item['nombre']}:** `{e}`")
        pass

    return None
