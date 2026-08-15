```markdown
# MunicipalWatch 📡

**MunicipalWatch** es un sistema automatizado en Python diseñado para monitorizar de forma periódica los tablones de anuncios y sedes electrónicas de diversos ayuntamientos. Permite rastrear novedades por municipio, extraer publicaciones mediante extractores modulares por plataforma y recibir alertas centralizadas.

---

## 🚀 Características

* **Arquitectura Modular:** Soporte para múltiples plataformas web de ayuntamientos mediante extractores independientes (`scrapers/`).
* **Configuración Externa:** Gestión sencilla de municipios y URLs desde un único archivo `ayuntamientos.json`.
* **Seguimiento Inteligente:** Guarda el histórico de publicaciones procesadas para evitar duplicados y reportar solo novedades reales.
* **Alertas Centralizadas:** Sistema unificado para gestionar y enviar notificaciones.

---

## 📁 Estructura del Proyecto

```text
municipalwatch/
├── ayuntamientos.json       # Configuración y lista de municipios a monitorizar
├── historial_ids.json       # Registro de estado (generado automáticamente)
├── pyproject.toml           # Configuración del paquete y dependencias
└── src/
    └── municipalwatch/
        ├── main.py          # Orquestador principal
        ├── notifier.py      # Gestor de notificaciones y salidas
        └── scrapers/        # Extractores específicos por tipo de plataforma
            ├── type_0.py    # Extractor Red de Sedes Región de Murcia
            └── __init__.py

```

---

## 🛠️ Instalación y Uso

### 1. Requisitos previos

Asegúrate de tener instalado **Python 3.9** o superior.

### 2. Clonar e instalar

```bash
# Clonar el repositorio
git clone [https://github.com/tu-usuario/municipalwatch.git](https://github.com/tu-usuario/municipalwatch.git)
cd municipalwatch

# Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar el paquete en modo editable con dependencias
pip install -e .

```

### 3. Configurar los municipios

Edita el archivo `ayuntamientos.json` para definir qué plataformas quieres monitorizar:

```json
[
  {
    "nombre": "Abanilla",
    "type": 0,
    "host": "sede.abanilla.regiondemurcia.es",
    "url": "[https://sede.abanilla.regiondemurcia.es/](https://sede.abanilla.regiondemurcia.es/)...",
    "referer": "[https://sede.abanilla.regiondemurcia.es/](https://sede.abanilla.regiondemurcia.es/)..."
  }
]

```

### 4. Ejecución

Puedes ejecutar el monitorizador mediante el comando registrado:

```bash
municipalwatch

```

O directamente ejecutando el módulo de Python:

```bash
python src/municipalwatch/main.py

```

---

## ⚙️ Añadir un Nuevo Tipo de Extractor

1. Crea un nuevo archivo en `src/municipalwatch/scrapers/type_X.py`.
2. Define la función de extracción que procese la página y devuelva el ID o dato único de la última publicación.
3. Regístralo en el diccionario `SCRAPERS` de `src/municipalwatch/scrapers/__init__.py`.
4. Asigna el tipo `"type": X` en tu `ayuntamientos.json`.

---

## 📄 Licencia

Este proyecto está bajo la Licencia [MIT](https://www.google.com/search?q=LICENSE).

```

```
