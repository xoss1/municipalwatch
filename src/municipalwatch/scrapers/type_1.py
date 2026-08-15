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

        # Buscar expedientes con la regex
        expedientes_std = re.findall(r'(\d+)/(\d{4})', html_text)
        #st.write(f"📑 **[DEBUG] Expedientes extraídos por Regex:** `{expedientes_std[:3]}`...")

        ids_encontrados = []
        for num, ano in expedientes_std:
            # Filtramos números coherentes de expedientes (evitar capturar fechas)
            if len(num) <= 5 and int(ano) >= 2020:
                ids_encontrados.append(int(f"{ano}{int(num):05d}"))

        if ids_encontrados:
            id_maximo = max(ids_encontrados)
            #st.success(f"✅ **[DEBUG] ID Máximo calculado para {item['nombre']}:** `{id_maximo}`")
            return id_maximo
        else:
            #st.warning(f"⚠️ **[DEBUG] No se pudo calcular ningún ID numérico para {item['nombre']}.**")

    except Exception as e:
        st.error(f"💥 **[DEBUG] Excepción capturada en {item['nombre']}:** `{e}`")

    return None
