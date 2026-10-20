"""
Punto de entrada de la app.  Ejecutar con:   streamlit run app.py

Este archivo solo arma el menú lateral y llama a la pantalla elegida.
Cada pantalla vive en la carpeta pantallas/ y tiene una función mostrar().
"""

import streamlit as st

from db import database
from pantallas import exportar, gimnasio, graficos, inicio, natacion, rutina

st.set_page_config(page_title="Entrenamiento", page_icon="🏋️", layout="wide")

# Se asegura de que existan las tablas (la primera vez crea la base).
database.crear_tablas()

# Menú: nombre visible -> función que dibuja la pantalla.
PANTALLAS = {
    "🏠 Inicio": inicio.mostrar,
    "🏋️ Gimnasio": gimnasio.mostrar,
    "🏊 Natación": natacion.mostrar,
    "📋 Rutina": rutina.mostrar,
    "📈 Gráficos": graficos.mostrar,
    "💾 Exportar": exportar.mostrar,
}

eleccion = st.sidebar.radio("Menú", list(PANTALLAS))
PANTALLAS[eleccion]()
