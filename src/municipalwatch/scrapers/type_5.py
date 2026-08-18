# src/municipalwatch/scrapers/type_5.py (AYTO MURCIA)
import re
import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime

def extract_type_5(session, item):
	"""Extractor para plataformas de la Red de Sedes de la Región de Murcia (Tipo 4)."""
	headers = {
	"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
	"Accept-encoding": "gzip, deflate, br, zstd",
	"Connection": "keep-alive",
	"Host": item["host"],
	"Referer": item["referer"],
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/151.0.0.0 Safari/537.36"
	}

	try:
		response = requests.get(item["url"])
		soup = BeautifulSoup(response.text, "html.parser")
		ids_encontrados = []
		# Seleccionar todas las tarjetas del tablón de anuncios
		cards = soup.select('.lista-anuncios-tablon .card')
		total_cards = len(cards)
		
		for index, card in enumerate(cards):
			# 1. Extraer el título del anuncio
			title_el = card.select_one('.card-body p.fw-bold:not(.text-red)')
			title = title_el.get_text(strip=True) if title_el else ""
			
			# 2. Extraer la fecha (ej: "Mar, 11/08/2026 - 00:00")
			time_el = card.select_one('time.datetime')
			if not time_el:
				continue
			
			date_raw = time_el.get_text(strip=True)
			# Extraer la fecha DD/MM/YYYY usando expresiones regulares
			match = re.search(r'(\d{2}/\d{2}/\d{4})', date_raw)
			
			if match:
				date_str = match.group(1)
				# Convertir a objeto datetime (a las 00:00:00)
				dt = datetime.strptime(date_str, "%d/%m/%Y")
				base_timestamp = int(dt.timestamp())
				
				# 3. Calcular ID Sintético Combinado:
				# Sumamos la posición invertida (total - índice) para que los primeros elementos del HTML
				# (más recientes) tengan un ID ligeramente superior dentro del mismo día.
				position_weight = total_cards - index
				synthetic_id = base_timestamp + position_weight
				ids_encontrados.append(synthetic_id)
				
				# Opción Alternativa Formateada: YYYYMMDD + 4 dígitos de posición inversa
				synthetic_id_formatted = int(f"{dt.strftime('%Y%m%d')}{position_weight:04d}")
		
				
				"""
				
				anuncios.append({
				'title': title[:60] + "..." if len(title) > 60 else title,
				'fecha': date_str,
				'synthetic_id': synthetic_id,
				'synthetic_id_formatted': synthetic_id_formatted
				})
				"""

	except Exception as e:
		print(f"   ❌ Error en extractor tipo 4 [{item['nombre']}]: {e}")
	return None
