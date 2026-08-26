import streamlit as st
import json
import os
import datetime
from datetime import datetime as dt
from datetime import time, timedelta
import requests
import re
from src.municipalwatch.scrapers import obtener_extractor
from scanner import ejecutar_escaneo

devMode = True

FICHERO_AYUNTAMIENTOS = "ayuntamientos.json"
FICHERO_HISTORIAL = "historial_ids.json"
FICHERO_NOVEDADES = "novedades.json"


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
        
def cargar_novedades():
    if os.path.exists(FICHERO_NOVEDADES):
        try:
            with open(FICHERO_NOVEDADES, "r", encoding="utf-8") as f:
                datos = json.load(f)
                # Garantizamos que devuelva una lista (si había un dict '{}', lo ignora)
                return datos if isinstance(datos, list) else []
        except (json.JSONDecodeError, Exception):
            return []
    return []
    
def guardar_novedades(novedades_nuevas):
    novedades_existentes = cargar_novedades()
    if novedades_nuevas:
        novedades_existentes.extend(novedades_nuevas)
    with open(FICHERO_NOVEDADES, "w", encoding="utf-8") as f:
        json.dump(novedades_existentes, f, indent=4, ensure_ascii=False)

def scan_reciente():

    if os.path.exists(FICHERO_NOVEDADES):
        if os.path.getsize(FICHERO_NOVEDADES) == 0:
            return False  # 🔥 fuerza escaneo

        mod_time = dt.fromtimestamp(os.path.getmtime(FICHERO_NOVEDADES))
        return dt.now() - mod_time < timedelta(hours=2)

    return False

def dentro_horario():
    ahora = dt.now()
    return (
        ahora.weekday() < 5 and
        time(7, 0) <= ahora.time() <= time(19, 0)
    )

def toca_ejecutar():
    ahora = dt.now()
    if "next_run" not in st.session_state:
        return True
    return ahora >= st.session_state.next_run

def fecha_en_rango(fecha_str, rango):
    """
    Comprueba si una fecha en texto está dentro del rango seleccionado.
    Convierte casi cualquier formato de fecha estándar.
    """
    if rango is None:
        return True
        
    if not fecha_str or str(fecha_str).strip() in ["N/A", "-", "None", ""]:
        return False  # Si no hay fecha válida, no entra en el rango de fechas específicas

    fecha_inicio, fecha_fin = rango
    fecha_obj = None
    
    # 1. Limpiar espacios extra
    cadena = str(fecha_str).strip()
    
    # 2. Extraer solo la parte de la fecha si viene con hora (ej: "22/08/2026 11:30" -> "22/08/2026")
    # Busca patrones tipo DD/MM/YYYY o YYYY-MM-DD
    match_dd_mm_yyyy = re.search(r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})', cadena)
    match_yyyy_mm_dd = re.search(r'(\d{4})[/\-](\d{1,2})[/\-](\d{1,2})', cadena)

    try:
        if match_dd_mm_yyyy:
            d, m, y = match_dd_mm_yyyy.groups()
            fecha_obj = dt(int(y), int(m), int(d)).date()
        elif match_yyyy_mm_dd:
            y, m, d = match_yyyy_mm_dd.groups()
            fecha_obj = dt(int(y), int(m), int(d)).date()
        else:
            # Fallback a formatos estándar directos
            for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%y"):
                try:
                    fecha_obj = dt.strptime(cadena, fmt).date()
                    break
                except ValueError:
                    continue
    except Exception:
        return False

    if fecha_obj is None:
        return False

    return fecha_inicio <= fecha_obj <= fecha_fin

# Interfaz Header
st.title("📡 MunicipalWatch")
st.caption("Panel de monitorización de edictos y tablones municipales")

# Cargar configuración
ayuntamientos = cargar_json(FICHERO_AYUNTAMIENTOS)
historial = cargar_json(FICHERO_HISTORIAL)

st.sidebar.header("⚙️ Configuración")
st.sidebar.info(f"Municipios configurados: **{len(ayuntamientos)}**")
if "last_run" in st.session_state:
    st.sidebar.info(f"🕒 Último escaneo: {st.session_state['last_run']}")

if "next_run" in st.session_state:
    st.sidebar.info(f"⏭ Próximo escaneo: {st.session_state['next_run']}")

# Desplegable para seleccionar el tipo de edictos a escanear
tipos_disponibles = [0, 1, 2, 3, 4, 5]
provincias_disponibles = ["MURCIA", "ALICANTE"]

if devMode:
    tipos_seleccionados = st.sidebar.multiselect(
        "Filtrar por tipo a escanear:",
        options=tipos_disponibles,
        default=tipos_disponibles,
        help="Selecciona los tipos (0 al 5) que deseas incluir en el escaneo."
    )
    
    provincias_seleccionadas = st.sidebar.multiselect(
        "Filtrar por provincia a escanear:",
        options=provincias_disponibles,
        default=provincias_disponibles,
        help="Selecciona la provincia que deseas incluir en el escaneo."
    )
else:
    tipos_seleccionados = tipos_disponibles
    provincias_seleccionadas = provincias_disponibles

# Definir la lista de opciones para el desplegable
opciones_periodo = [
    "Solo hoy",
    "Hoy y ayer",
    "Últimos 7 días",
    "Últimos 30 días",
    "Todas las fechas"
]
# Desplegable de selección única
periodo_seleccionado = st.sidebar.selectbox(
    "Filtrar por fecha de publicación:",
    options=opciones_periodo,
    index=3,  # Selecciona "Últimos 30 días" por defecto
    help="Las novedades se filtrarán instantáneamente sin necesidad de re-escanear."
)

hoy = datetime.date.today()

if periodo_seleccionado == "Solo hoy":
    rango_fechas = (hoy, hoy)

elif periodo_seleccionado == "Hoy y ayer":
    ayer = hoy - datetime.timedelta(days=1)
    rango_fechas = (ayer, hoy)

elif periodo_seleccionado == "Últimos 7 días":
    hace_7_dias = hoy - datetime.timedelta(days=7)
    rango_fechas = (hace_7_dias, hoy)

elif periodo_seleccionado == "Últimos 30 días":
    hace_30_dias = hoy - datetime.timedelta(days=30)
    rango_fechas = (hace_30_dias, hoy)

else:  # "Todas las fechas"
    rango_fechas = None

# Toggle de la barra lateral
expandir_todos = st.sidebar.toggle("Abrir / Cerrar todos", value=False)

scanReciente = scan_reciente()

if devMode == True:
    lanzar = st.button("🚀 Iniciar Escaneo de Edictos", type="primary")
    scanReciente = False
else:
    lanzar = False
    if dentro_horario() and toca_ejecutar():
        lanzar = True

novedades = cargar_novedades()
# Botón de escaneo
if lanzar and not scanReciente:
    progress_bar = st.progress(0)

    def actualizar_progreso(valor):
        progress_bar.progress(valor)
    novedades_temp, historial = ejecutar_escaneo(
        ayuntamientos,
        historial,
        tipos_seleccionados,
        provincias_seleccionadas,
        progress_callback=actualizar_progreso      
    )
            
    guardar_historial(historial)
    # Guardamos las novedades en session_state para que NO desaparezcan al pulsar botones o toggles
    st.session_state["novedades"] = novedades_temp
    guardar_novedades(novedades_temp)
    ahora = dt.now() + timedelta(hours=2) 
    st.session_state["last_run"] = ahora
    st.session_state["next_run"] = ahora + timedelta(hours=2)
    
    st.divider()

if "novedades" not in st.session_state:
    st.session_state["novedades"] = cargar_novedades()

# Renderizado de Resultados
novedades = st.session_state.get("novedades", cargar_novedades())

# Resultados
if novedades:
    print(novedades)
    for prov in provincias_seleccionadas:
        st.markdown(f"**PROVINCIA: {prov}**")
        novedades_provincia = [nov for nov in novedades if nov.get("provincia") == prov]
        for nov in novedades_provincia:
            # Obtener la lista de items/bloques extraídos
            contenido = nov.get("contenido")
            
            if contenido:
                # Filtrar o mostrar únicamente las novedades
                novedades_visibles = []
                for item in contenido:
                    fecha_pub = item.get("fecha_pub")
                    
                    # Opcional: Filtra por ítems con ID estrictamente superior al anterior
                    if fecha_en_rango(fecha_pub, rango_fechas):
                        novedades_visibles.append((item, fecha_pub))

                if novedades_visibles:
                    url_tablon = nov['referer'] if nov['tipo'] in (0, 3) else nov['url']
                    label_expander = f"📍 {nov['seccion']} ({len(novedades_visibles)}) | [🔗 ver tablón de edictos]({url_tablon})"
                    
                    # Key única: incluye el índice del municipio y la opción de periodo para reactivar el filtro
                    key_expander = f"exp_{nov['seccion']}_{nov['id_nuevo']}_{expandir_todos}"
                    
                    with st.expander(
                        label_expander, 
                        expanded=expandir_todos,
                        key=key_expander
                    ):
                        st.caption(f"ID Anterior: `{nov['id_anterior']}` ➔ ID Nuevo: `{nov['id_nuevo']}`")
                        
                        # 3. DIBUJAR CADA EDICTO DENTRO DEL EXPANDER
                        for item, fecha_pub in novedades_visibles:
                            st.caption(f"{nov['seccion']}")
                            col1, col2 = st.columns([1, 4])
                            with col1:
                                st.markdown(f"**ID:** `{item.get('id', '-')}`")
                                st.caption(f"Exp: {item.get('cod_exp', '-')}")
                            with col2:
                                st.markdown(f"**{item.get('titulo', '-')}**")
                                st.text(f"Publicación: {fecha_pub or '-'} | Retirada: {item.get('fecha_ret', '-')}")
                            st.divider()
                else:
                    #st.write("No hay detalles desglosados disponibles para esta sección.")
                    pass
else:
    st.info("Cero novedades en todas las páginas rastreadas.")
# Vista rápida del historial guardado
#st.divider()
#st.subheader("📋 Registro de Últimos IDs Almacenados")
#if historial:
#    st.json(historial)
#else:
#    st.write("Aún no hay historial registrado. Haz clic en 'Iniciar Escaneo'.")
