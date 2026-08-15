# src/municipalwatch/main.py
import json
import os
import time
import requests
from scrapers import obtener_extractor
from notifier import notificar_novedades

FICHERO_AYUNTAMIENTOS = "ayuntamientos.json"
FICHERO_HISTORIAL = "historial_ids.json"

def cargar_json(ruta):
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    return {} if "historial" in ruta else []

def guardar_historial(historial):
    with open(FICHERO_HISTORIAL, "w", encoding="utf-8") as f:
        json.dump(historial, f, indent=4, ensure_ascii=False)

def monitorizar_todos():
    ayuntamientos = cargar_json(FICHERO_AYUNTAMIENTOS)
    historial = cargar_json(FICHERO_HISTORIAL)
    session = requests.Session()
    novedades = []

    print(f"🔍 Iniciando escaneo de {len(ayuntamientos)} ayuntamientos...\n")

    REMPLAZOS = str.maketrans("áéíóúÁÉÍÓÚñÑ", "aeiouAEIOUnN")
    ayuntamientos = sorted(ayuntamientos, key=lambda x: x["nombre"].translate(REMPLAZOS).lower())

    for item in ayuntamientos:
        nombre = item["nombre"]
        tipo = item["type"]
        
        print(f"📡 Comprobando: [{nombre}] (Tipo {tipo})")
        extractor = obtener_extractor(tipo)

        if not extractor:
            print(f"   ⚠️ Extractor tipo {tipo} no implementado.")
            continue

        id_actual = extractor(session, item)

        if id_actual is not None:
            id_anterior = historial.get(nombre, 0)
            if id_actual > id_anterior:
                novedades.append({
                    "seccion": nombre,
                    "id_nuevo": id_actual,
                    "id_anterior": id_anterior,
                    "url": item["url"]
                })
                historial[nombre] = id_actual
                print(f"   🔥 ¡Novedad detectada! (ID {id_anterior} -> {id_actual})")
            else:
                print("   - Sin novedades.")
        else:
            print("   - No se pudo consultar la página.")

        time.sleep(3)
        print("-" * 50)

    guardar_historial(historial)
    notificar_novedades(novedades)

if __name__ == "__main__":
    monitorizar_todos()
