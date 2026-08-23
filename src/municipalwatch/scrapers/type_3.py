from curl_cffi import requests
import re
import requests as req
import time
import streamlit as st
import json

def extract_type_3(session, item):
    """Extractor para plataformas Tipo 3 ("Carpeta Ciudadana") con depuración en tiempo real."""
    url = item["url"]
    nombre = item["nombre"]
    rootid = ""
    eventscreenId = ""
    pagecode = ""
    hfc = ""
    esMazarron = False
    esAlhama = False
    esElche = False

    if nombre == "Molina de Segura":
        rootid = "31"
        eventscreenId = "TABLON"
        pagecode = "TABLON"
        hfc = "HEADER_OVC#FOOTER_OVC"
    elif nombre == "Mazarrón":
        esMazarron = True
    elif nombre == "Alhama de Murcia":
        esAlhama = True
    elif nombre == "Elche":
        esElche = True
    elif nombre in ("San Pedro del Pinatar", "Novelda"):
        rootid = "2"
        eventscreenId = "PTS_TABLON"
        pagecode = "PTS_TABLON"
        hfc = "HEADER_PTS#FOOTER_PTS"
    elif nombre in ("Torre-Pacheco", "Pilar de la Horadada", "Elche"):
        rootid = "1"
        eventscreenId = "PTS2_TABLON"
        pagecode = "PTS2_TABLON"
        hfc = "HEADER#FOOTER"

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
        "eventScreenId": eventscreenId,
        "eventComponent": "",
        "eventObject": "LISTATABLON",
        "eventAction": "LISTATABLON",
        "eventArguments": "KEY=all",
        "PAGE_CODE": pagecode,
        "APP_CODE": "STA",
        "PAGE_COMPLETE": "",
        "ROOTID": rootid,
        "HFC": hfc,
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
            if esElche:
                session = req.Session()
                session.verify = False
            else:
                session = requests.Session()
                session.verify = False
                session_aa = session.get(url, impersonate="chrome", proxies=proxies, verify=False)
                time.sleep(1)
                #st.write(f"🔍 **[DEBUG] Estatus de sesion GET {session_aa.status_code}:** `{url}`")
                #st.write(f"🔍 **[DEBUG] Escaneando {nombre}:** `{url}`")

            if esMazarron or esAlhama:
                response = requests.get(item["referer"], proxies=proxies, verify=False)
            elif esElche:
                response = session.get(item["referer"], proxies=proxies, verify=False)
            else:
                response = requests.post(url, proxies=proxies, data=payload, verify=False)
            #st.write(f"👉 **[DEBUG] Código HTTP respuesta:** `{response.status_code}`")
    
            if response.status_code != 200:
                st.error(f"❌ La web devolvió un estado no válido: {response.status_code}")
                return None
    
            html_text = response.text
            #st.write(f"📄 **[DEBUG] Longitud del HTML recibido:** `{len(html_text)}` caracteres")
    
            ids_encontrados = []
            resultados = []
            match = re.search(r'var\s+\w+\s*=\s*(\[\s*\{.*?\}\s*\]);', html_text, re.DOTALL)

            if match:
                data = json.loads(match.group(1))
            
                for d in data:
                    dboid = d.get("dboid")
                    descriptionProc = d.get("descriptionProc")
                    externString = d.get("externString")
            
                    pubDateIni = d.get("pubDateIni", {})
                    pubDateFin = d.get("pubDateFin")

                    fecha_str = f"{int(pubDateIni['year']):04d}{int(pubDateIni['month']):02d}{int(pubDateIni['day']):02d}{int(pubDateIni['hour']):02d}{int(pubDateIni['minute']):02d}{int(pubDateIni['second']):02d}"
                    bloque_unico = dboid[8:-5]
                    id_sintetico = int(f"{fecha_str}{bloque_unico}")
                    ids_encontrados.append(id_sintetico)
                    fecha_pub = f"{int(pubDateIni['day']):02d}/{int(pubDateIni['month']):02d}/{int(pubDateIni['year']):04d}"
                    if pubDateFin:
                        fecha_ret = f"{int(pubDateFin['day']):02d}/{int(pubDateFin['month']):02d}/{int(pubDateFin['year']):04d}"
                    else:
                        fecha_ret = "N/A"
                    bloque = {
                        "id": id_sintetico,
                        "fecha_publicacion": fecha_pub,
                        "fecha_retirada": fecha_ret,
                        "titulo": descriptionProc,
                        "codigo_expediente": externString
                    }
                    resultados.append(bloque)

            #st.write(f"📄 **[DEBUG] id encontrados:** '{ids_encontrados}'")
            if ids_encontrados and resultados:
                return [resultados, max([int(i) for i in ids_encontrados])]
        except Exception as e:
            st.error(f"💥 **[DEBUG] Excepción capturada en {nombre}:** `{e}`")
            pass

    return None
