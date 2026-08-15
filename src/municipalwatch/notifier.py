# src/municipalwatch/notifier.py
def notificar_novedades(novedades):
    """Centraliza la salida de los resultados."""
    print("\n================ RESUMEN DE NOVEDADES ================")
    if novedades:
        print(f"🔥 Se encontraron cambios en {len(novedades)} entidad(es):\n")
        for nov in novedades:
            print(f"• {nov['seccion']}: ID subió de {nov['id_anterior']} ➔ {nov['id_nuevo']}")
            print(f"  URL: {nov['url']}\n")
    else:
        print("Cero novedades en todas las páginas rastreadas.")
