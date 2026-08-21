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
    help="Selecciona los tipos (0 al 5) que deseas incluir en el escaneo."
)

# Botón de escaneo
if st.button("🚀 Iniciar Escaneo de Edictos", type="primary"):
    if not tipos_seleccionados:
        st.warning("⚠️ Debes seleccionar al menos un tipo en la barra lateral.")
    else:
        session = requests.Session()
        novedades = []
        
        # Filtrar ayuntamientos según los tipos seleccionados
        ayuntamientos_filtrados = [item for item in ayuntamientos if item.get("type") in tipos_seleccionados]
        
        if not ayuntamientos_filtrados:
            st.info("No se encontraron municipios con los tipos seleccionados.")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()

            REMPLAZOS = str.maketrans("áéíóúÁÉÍÓÚñÑ", "aeiouAEIOUnN")
            ayuntamientos_filtrados = sorted(
                ayuntamientos_filtrados, 
                key=lambda x: x["nombre"].translate(REMPLAZOS).lower()
            )
            
            for idx, item in enumerate(ayuntamientos_filtrados):
                nombre = item["nombre"]
                tipo = item["type"]
                url = item["url"]
                referer = item["referer"]
                
                status_text.text(f"Escaneando: {nombre} (Tipo {tipo})...")
                
                extractor = obtener_extractor(tipo)
                if extractor:
                    extracto = extractor(session, item)
                    
                    # Manejo flexible por si el extractor retorna un int o [resultados, id_maximo]
                    if isinstance(extracto, (list, tuple)):
                        id_actual = extracto[1]
                        resultados = extracto[0]


                    if id_actual is not None:
                        id_anterior = historial.get(nombre, 0)
                        if id_actual > id_anterior:
                            for item in resultados:
                                novedades.append({
                                    "titulo": item["titulo"],
                                    "id": item["id"],
                                    "fecha_pub": item["fecha_publicacion"],
                                    "fecha_ret": item["fecha_retirada"],
                                    "cod_ext": item["codigo_expediente"],
                                    "url": url,
                                    "referer": referer,
                                    "tipo": tipo,
                                    "seccion": nombre
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
                    # Determinación de la URL destino según el tipo
                    url_tablon = nov['referer'] if nov['tipo'] in (0, 3) else nov['url']
                    
                    # Cabecera con Nombre y Enlace
                    label_expander = f"📍 {nov['seccion']} | [🔗 ver tablón de edictos]({url_tablon})"
                    
                    with st.expander(label_expander):
                        st.caption(f"ID Anterior: `{nov['id_anterior']}` ➔ ID Nuevo: `{nov['id_nuevo']}`")
                        
                        # Obtener la lista de items/bloques extraídos
                        lista_items = nov.get("items", [])
                        
                        if lista_items:
                            # Filtrar o mostrar únicamente las novedades
                            for item in lista_items:
                                # Opcional: Filtra por ítems con ID estrictamente superior al anterior
                                if item.get("id", 0) > nov['id_anterior']:
                                    col1, col2 = st.columns([1, 4])
                                    with col1:
                                        st.markdown(f"**ID:** `{item.get('id', '-')}`")
                                        st.caption(f"Exp: {item.get('codigo_expediente', '-')}")
                                    with col2:
                                        st.markdown(f"**{item.get('titulo', '-')}**")
                                        st.text(f"Publicación: {item.get('fecha_publicacion', '-')} | Retirada: {item.get('fecha_retirada', '-')}")
                                    st.divider()
                        else:
                            st.write("No hay detalles desglosados disponibles para esta sección.")
            else:
                st.info("Cero novedades en todas las páginas rastreadas.")
# Vista rápida del historial guardado
st.divider()
st.subheader("📋 Registro de Últimos IDs Almacenados")
if historial:
    st.json(historial)
else:
    st.write("Aún no hay historial registrado. Haz clic en 'Iniciar Escaneo'.")
