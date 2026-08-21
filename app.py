import streamlit as st
import json
import os
import requests
from src.municipalwatch.scrapers import obtener_extractor

FICHERO_AYUNTAMIENTOS = "ayuntamientos.json"
FICHERO_HISTORIAL = "historial_ids.json"

st.set_page_config(
    page_title="MunicipalWatch",
    page_icon="📡",
    layout="wide"
)

# Carga de datos
def cargar_json(ruta):
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    return {} if "historial" in ruta else []

def guardar_historial(historial):
    with open(FICHERO_HISTORIAL, "w", encoding="utf-8") as f:
        json.dump(historial, f, indent=4, ensure_ascii=False)

# Interfaz Header
st.title("📡 MunicipalWatch")
st.caption("Panel de monitorización de edictos y tablones municipales")

# Cargar configuración
ayuntamientos = cargar_json(FICHERO_AYUNTAMIENTOS)
historial = cargar_json(FICHERO_HISTORIAL)

st.sidebar.header("⚙️ Configuración")
st.sidebar.info(f"Municipios configurados: **{len(ayuntamientos)}**")

# Desplegable para seleccionar el tipo de edictos a escanear
tipos_disponibles = [0, 1, 2, 3, 4, 5]
tipos_seleccionados = st.sidebar.multiselect(
    "Filtrar por tipo a escanear:",
    options=tipos_disponibles,
    default=tipos_disponibles,
    help="Selecciona uno o varios tipos (0 al 5) para limitar el escaneo."
)

# Botón de escaneo
if st.button("🚀 Iniciar Escaneo de Edictos", type="primary"):
    if not tipos_seleccionados:
        st.warning("⚠️ Debes seleccionar al menos un tipo en la barra lateral para iniciar el escaneo.")
    else:
        session = requests.Session()
        novedades = []
        
        # Filtrar ayuntamientos según los tipos seleccionados en el desplegable
        ayuntamientos_filtrados = [item for item in ayuntamientos if item.get("type") in tipos_seleccionados]
        
        if not ayuntamientos_filtrados:
            st.info("No hay ayuntamientos configurados con el/los tipo(s) seleccionado(s).")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()

            REMPLAZOS = str.maketrans("áéíóúÁÉÍÓÚñÑ", "aeiouAEIOUnN")
            ayuntamientos_filtrados = sorted(ayuntamientos_filtrados, key=lambda x: x["nombre"].translate(REMPLAZOS).lower())
            
            for idx, item in enumerate(ayuntamientos_filtrados):
                nombre = item["nombre"]
                tipo = item["type"]
                
                status_text.text(f"Escaneando: {nombre} (Tipo {tipo})...")
                
                extractor = obtener_extractor(tipo)
                if extractor:
                    resultado_extractor = extractor(session, item)
                    
                    # Manejo flexible por si el extractor retorna int o tuple/list [resultados, max_id]
                    if isinstance(resultado_extractor, (list, tuple)):
                        id_actual = resultado_extractor[1]
                    else:
                        id_actual = resultado_extractor

                    if id_actual is not None:
                        id_anterior = historial.get(nombre, 0)
                        if id_actual > id_anterior:
                            novedades.append({
                                "seccion": nombre,
                                "id_nuevo": id_actual,
                                "id_anterior": id_anterior,
                                "url": item["url"],
                                "referer": item["referer"],
                                "tipo": item["type"]
                            })
                            historial[nombre] = id_actual
                
                progress_bar.progress((idx + 1) / len(ayuntamientos_filtrados))
            
            guardar_historial(historial)
            status_text.text("✅ Escaneo finalizado.")
            
            st.divider()
            
            # Resultados
            if novedades:
                st.success(f"🔥 ¡Novedades detectadas en {len(novedades)} municipio(s)!")
                for nov in novedades:
                    with st.expander(f"📍 {nov['seccion']} (Nuevo ID: {nov['id_nuevo']})"):
                        st.write(f"**ID Anterior:** {nov['id_anterior']} ➔ **ID Nuevo:** {nov['id_nuevo']}")
                        if nov['tipo'] in (0, 3):
                            st.markdown(f"[🔗 Ver tablón de edictos]({nov['referer']})")
                        else:
                            st.markdown(f"[🔗 Ver tablón de edictos]({nov['url']})")
            else:
                st.info("Cero novedades en todas las páginas rastreadas.")# Vista rápida del historial guardado
st.divider()
st.subheader("📋 Registro de Últimos IDs Almacenados")
if historial:
    st.json(historial)
else:
    st.write("Aún no hay historial registrado. Haz clic en 'Iniciar Escaneo'.")
