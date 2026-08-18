# src/municipalwatch/scrapers/__init__.py
from .type_0 import extract_type_0
from .type_1 import extract_type_1
from .type_2 import extract_type_2
from .type_3 import extract_type_3
from .type_4 import extract_type_4
from -type_5 import extract_type_5

# Mapeo extensible: cuando crees la plataforma tipo 1, solo agregas "1: extract_type_1"
SCRAPERS = {
    0: extract_type_0,
    1: extract_type_1,
    2: extract_type_2,
    3: extract_type_3,
    4: extract_type_4,
    5: extract_type_5
}

def obtener_extractor(tipo_plataforma):
    return SCRAPERS.get(tipo_plataforma)
