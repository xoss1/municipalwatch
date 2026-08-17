import re
import streamlit as st

def extract_type_3(session, item):
    """Extractor para plataformas Tipo 3 ("Carpeta Ciudadana") con depuración en tiempo real."""
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive",
        "Host": item.get("host", ""),
        "Referer": item.get("referer", ""),
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"
    }

    payload = {
        "aaxmlrequest": "true",
        "eventScreenId": "TABLON",
        "eventComponent": "",
        "eventObject": "LISTATABLON",
        "eventAction": "LISTATABLON",
        "eventArguments": "KEY=all",
        "PAGE_CODE": "TABLON",
        "APP_CODE": "STA",
        "PAGE_COMPLETE": "",
        "ROOTID": "31",
        "HFC": "HEADER_OVC#FOOTER_OVC",
        "SESSION_REQUIRED": "false"
    }

    try:
        session.get(item["referer"], timeout=10)
        time.sleep(1)
        url = item["url"]
        st.write(f"🔍 **[DEBUG] Escaneando {item['nombre']}:** `{url}`")
        
        response = session.post(url, data=payload, headers=headers, timeout=15, allow_redirects=True)
        st.write(f"👉 **[DEBUG] Código HTTP respuesta:** `{response.status_code}`")

        if response.status_code != 200:
            st.error(f"❌ La web devolvió un estado no válido: {response.status_code}")
            return None

        html_text = response.text
        st.write(f"📄 **[DEBUG] Longitud del HTML recibido:** `{len(html_text)}` caracteres")

        ids_encontrados = []

        pattern = re.compile(
            r'(?:\[\s*\{|,\s*\{)\s*'                      # Coincide con [{ o ,{ (inicio de elemento en el array)
            r'"dboid"\s*:\s*"(?P<dboid>\d+)".*?'          # Captura solo el DBOID principal del objeto
            r'"pubDateIni"\s*:\s*\{\s*'
            r'"year"\s*:\s*(?P<year>\d+)\s*,\s*'
            r'"month"\s*:\s*(?P<month>\d+)\s*,\s*'
            r'"day"\s*:\s*(?P<day>\d+)\s*,\s*'
            r'"timezone"\s*:\s*\d+\s*,\s*'
            r'"hour"\s*:\s*(?P<hour>\d+)\s*,\s*'
            r'"minute"\s*:\s*(?P<minute>\d+)\s*,\s*'
            r'"second"\s*:\s*(?P<second>\d+)',
            re.DOTALL
        )

        for match in pattern.finditer(texto_dataset):
            d = match.groupdict()
    
            fecha_str = f"{int(d['year']):04d}{int(d['month']):02d}{int(d['day']):02d}{int(d['hour']):02d}{int(d['minute']):02d}{int(d['second']):02d}"
            bloque_unico = d['dboid'][8:-5]
    
            id_sintetico = int(f"{fecha_str}{bloque_unico}")
            ids_sinteticos.append(id_sintetico)
            
        st.write(f"📄 **[DEBUG] id encontrados:** '{ids_encontrados}'")
        if ids_encontrados:
            return max([int(i) for i in ids_encontrados])
    except Exception as e:
        st.error(f"💥 **[DEBUG] Excepción capturada en {item['nombre']}:** `{e}`")
        pass

    return None
