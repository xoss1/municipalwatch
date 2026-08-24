import requests
from src.municipalwatch.scrapers import obtener_extractor

def ejecutar_escaneo(ayuntamientos, historial, tipos, provincias, progress_callback=None):

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
              if progress_callback:
                progress_callback((idx + 1) / len(ayuntamientos_filtrados))
  return novedades_temp, historial
