import streamlit as st
import json
import os
import datetime
from datetime import datetime as dt
import requests
from src.municipalwatch.scrapers import obtener_extractor

FICHERO_AYUNTAMIENTOS = "ayuntamientos.json"
FICHERO_HISTORIAL = "historial_ids.json"

hoy = datetime.date.today()
ayer = hoy - datetime.timedelta(days=1)
hace_7_dias = hoy - datetime.timedelta(days=7)
hace_30_dias = hoy - datetime.timedelta(days=30)

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

def fecha_en_rango(fecha_str, rango):
    if not fecha_str or fecha_str in ["N/A", "-"]:
        return True
    
    if isinstance(rango, (list, tuple)):
        if len(rango) == 1:
            fecha_inicio = rango[0]
            fecha_fin = rango[0]
        elif len(rango) == 2:
            fecha_inicio, fecha_fin = rango
        else:
            return True
    else:
        return True

    fecha_obj = None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            fecha_obj = dt.strptime(fecha_str.strip(), fmt).date()
            break
        except ValueError:
            continue

    if fecha_obj is None:
        try:
            fecha_obj = dt.strptime(fecha_str.split()[0], "%d/%m/%Y").date()
        except Exception:
            return True
            
    return fecha_inicio <= fecha_obj <= fecha_fin

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

provincias_disponibles = ["MURCIA", "ALICANTE"]
provincias_seleccionadas = st.sidebar.multiselect(
    "Filtrar por provincia a escanear:",
    options=provincias_disponibles,
    default=provincias_disponibles,
    help="Selecciona la provincia que deseas incluir en el escaneo."
)

st.sidebar.subheader("Filtro Visual")
rango_fechas = st.sidebar.date_input(
    "Filtrar por fecha de publicación:",
    value=(hoy, ayer, hace_7_dias, hace_30_dias),
    help="Las novedades se filtrarán instantáneamente sin necesidad de re-escanear."
)

# Toggle de la barra lateral
expandir_todos = st.sidebar.toggle("Abrir / Cerrar todos", value=False)

# Botón de escaneo
if st.button("🚀 Iniciar Escaneo de Edictos", type="primary"):
    if not tipos_seleccionados:
        st.warning("⚠️ Debes seleccionar al menos un tipo en la barra lateral.")
    elif not provincias_seleccionadas:
        st.warning("⚠️ Debes seleccionar al menos una provincia en la barra lateral.")
    else:
        session = requests.Session()
        novedades_temp = []
        
        # Filtrar ayuntamientos según los tipos seleccionados
        ayuntamientos_filtrados = [item for item in ayuntamientos if item.get("type") in tipos_seleccionados and item.get("provincia") in provincias_seleccionadas]
        
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
                provincia = item["provincia"]
                
                status_text.text(f"Escaneando: {nombre} (Tipo {tipo})...")
                
                extractor = obtener_extractor(tipo)
                if extractor:
                    extracto = extractor(session, item)
                    
                    # Manejo flexible por si el extractor retorna un int o [resultados, id_maximo]
                    if isinstance(extracto, (list, tuple)):
                        id_actual = extracto[1]
                        resultados = extracto[0]
                    else:
                        id_actual = None
                        resultados = False

                    if resultados and id_actual is not None:
                        id_anterior = historial.get(nombre, 0)
                        if id_actual > id_anterior:
                            contenido = []
                            for res in resultados:
                                contenido.append({
                                    "titulo": res["titulo"],
                                    "id": res["id"],
                                    "fecha_pub": res["fecha_publicacion"],
                                    "fecha_ret": res["fecha_retirada"],
                                    "cod_exp": res["codigo_expediente"]
                                })
                            novedades_temp.append({
                                "id_anterior": id_anterior,
                                "id_nuevo": id_actual,
                                "url": url,
                                "referer": referer,
                                "tipo": tipo,
                                "seccion": nombre,
                                "provincia": provincia,
                                "contenido": contenido
                            })
                            historial[nombre] = id_actual
                    else:
                        pass

                progress_bar.progress((idx + 1) / len(ayuntamientos_filtrados))
            
        guardar_historial(historial)
        status_text.text("✅ Escaneo finalizado.")
        # Guardamos las novedades en session_state para que NO desaparezcan al pulsar botones o toggles
        st.session_state["novedades"] = novedades_temp
        
        st.divider()

# Renderizado de Resultados
novedades = st.session_state.get("novedades", [])

# Resultados
if novedades:
    st.success(f"🔥 ¡Novedades detectadas en {len(st.session_state.novedades)} municipio(s)!")
    for prov in provincias_seleccionadas:
        st.markdown(f"**PROVINCIA: {prov}**")
        novedades_provincia = [nov for nov in novedades if nov.get("provincia") == prov]
        for nov in novedades_provincia:
            # Determinación de la URL destino según el tipo
            url_tablon = nov['referer'] if nov['tipo'] in (0, 3) else nov['url']
            
            # Cabecera con Nombre y Enlace
            label_expander = f"📍 {nov['seccion']} | [🔗 ver tablón de edictos]({url_tablon})"
            
            # Se asigna dinámicamente según el estado del toggle
            with st.expander(
                label_expander, 
                expanded=expandir_todos,
                key=f"exp_{nov['seccion']}_{nov['id_nuevo']}_{expandir_todos}"
            ):
                st.caption(f"ID Anterior: `{nov['id_anterior']}` ➔ ID Nuevo: `{nov['id_nuevo']}`")
                
                # Obtener la lista de items/bloques extraídos
                contenido = nov.get("contenido")
                
                if contenido:
                    # Filtrar o mostrar únicamente las novedades
                    for item in contenido:
                        # Opcional: Filtra por ítems con ID estrictamente superior al anterior
                        if fecha_en_rango(item.get("f_pub"), rango_fechas):
                            st.caption(f"{nov['seccion']}")
                            col1, col2 = st.columns([1, 4])
                            with col1:
                                st.markdown(f"**ID:** `{item.get('id', '-')}`")
                                st.caption(f"Exp: {item.get('cod_exp', '-')}")
                            with col2:
                                st.markdown(f"**{item.get('titulo', '-')}**")
                                st.text(f"Publicación: {item.get('fecha_pub', '-')} | Retirada: {item.get('fecha_ret', '-')}")
                            st.divider()
                else:
                    st.write("No hay detalles desglosados disponibles para esta sección.")
elif "novedades" in st.session_state:
    st.info("Cero novedades en todas las páginas rastreadas.")
# Vista rápida del historial guardado
#st.divider()
#st.subheader("📋 Registro de Últimos IDs Almacenados")
#if historial:
#    st.json(historial)
#else:
#    st.write("Aún no hay historial registrado. Haz clic en 'Iniciar Escaneo'.")
