import re
import streamlit as st

def extract_type_2(session, item):
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

        ids_encontrados = re.findall(r'anuncio\.aspx\?id=(\d+)', html_text)
        if ids_encontrados:
            return max([int(i) for i in ids_encontrados])
    except Exception as e:
        #st.error(f"💥 **[DEBUG] Excepción capturada en {item['nombre']}:** `{e}`")
        pass

    return None
