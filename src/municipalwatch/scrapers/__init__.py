# src/municipalwatch/scrapers/__init__.py
from .type_0 import extract_type_0

# Mapeo extensible: cuando crees la plataforma tipo 1, solo agregas "1: extract_type_1"
SCRAPERS = {
    0: extract_type_0
}

def obtener_extractor(tipo_plataforma):
    return SCRAPERS.get(tipo_plataforma)
