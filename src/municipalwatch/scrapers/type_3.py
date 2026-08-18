from curl_cffi import requests
import time
import streamlit as st

def extract_type_3(session, item):
    """Extractor para plataformas Tipo 3 ("Carpeta Ciudadana") con depuración en tiempo real."""
    url = item["url"]
    headers = {
        "Accept": "text/xml",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "es-ES,es;q=0.9",
        "Connection": "keep-alive",
        "Content-Length": "234",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Host": item["host"],
        "Origin": "https://"+item["host"],
        "Referer": item["referer"],
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
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

    lista_proxies = [
        "http://hfzpvcaa:s4s7wxrw1fv1@64.137.96.74:6641/",
        "http://hfzpvcaa:s4s7wxrw1fv1@31.59.20.176:6754/",
        "http://hfzpvcaa:s4s7wxrw1fv1@31.56.127.193:7684/",
        "http://hfzpvcaa:s4s7wxrw1fv1@45.38.107.97:6014/",
        "http://hfzpvcaa:s4s7wxrw1fv1@198.105.121.200:6462/",
        "http://hfzpvcaa:s4s7wxrw1fv1@198.23.243.226:6361/",
        "http://hfzpvcaa:s4s7wxrw1fv1@38.154.185.97:6370/",
        "http://hfzpvcaa:s4s7wxrw1fv1@84.247.60.125:6095/",
        "http://hfzpvcaa:s4s7wxrw1fv1@142.111.67.146:5611/",
        "http://hfzpvcaa:s4s7wxrw1fv1@191.96.254.138:6185/"
    ]

    for proxy in lista_proxies:
        
        proxies = {
        "http": proxy, 
        "https": proxy
    }
        try:
            session = requests.Session()
            session_aa = session.get(url, impersonate="chrome", proxies=proxies)
            time.sleep(1)
            st.write(f"🔍 **[DEBUG] Estatus de sesion GET {session_aa.status_code}:** `{url}`")
            st.write(f"🔍 **[DEBUG] Escaneando {item['nombre']}:** `{url}`")
            
            response = requests.post(url, proxies=proxies, data=payload)
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
