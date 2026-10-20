"""Pantalla de inicio: resumen rápido y alertas."""

from datetime import date, timedelta

import streamlit as st

from db import database
from db.datos_ejemplo import cargar_datos_ejemplo
from logica.progresion import detectar_estancamientos


def mostrar():
    st.title("🏠 Mi entrenamiento")

    # Si la base está vacía, ofrecemos cargar datos de ejemplo.
    if database.base_vacia():
        st.info("Todavía no hay registros. Podés empezar a cargar o probar con datos de ejemplo.")
        semanas = st.number_input("Semanas de ejemplo", min_value=1, max_value=12, value=2)
        if st.button("Cargar datos de ejemplo"):
            cargar_datos_ejemplo(int(semanas))
            st.rerun()
        return

    series_df = database.leer_series_gym()
    natacion_df = database.leer_natacion()

    # Métricas de los últimos 7 días
    hace_una_semana = date.today() - timedelta(days=7)
    gym_semana = series_df[series_df["fecha"].dt.date > hace_una_semana]
    nat_semana = natacion_df[natacion_df["fecha"].dt.date > hace_una_semana]

    col1, col2, col3 = st.columns(3)
    col1.metric("Días de gimnasio (7 días)", gym_semana["fecha"].nunique())
    col2.metric("Series hechas (7 días)", len(gym_semana))
    col3.metric("Metros nadados (7 días)", f"{int(nat_semana['metros'].sum()):,}".replace(",", "."))

    # Alertas de estancamiento
    st.subheader("Alertas")
    alertas = detectar_estancamientos(series_df)
    if not alertas:
        st.success("Sin estancamientos: todo progresando 💪")
    for a in alertas:
        st.warning(
            f"**{a['ejercicio']}** no progresa hace 3 sesiones "
            f"(1RM estimado reciente {a['mejor_reciente']:g} kg vs. mejor previo {a['mejor_previo']:g} kg). "
            "Probá una semana de descarga, cambiar el rango de reps o revisar técnica/descanso."
        )

    # Última actividad
    st.subheader("Última actividad")
    if not series_df.empty:
        ultima = series_df["fecha"].max()
        st.write(f"🏋️ Gimnasio: {ultima:%d/%m/%Y}")
    if not natacion_df.empty:
        ultima = natacion_df.iloc[-1]
        st.write(f"🏊 Natación: {ultima['fecha']:%d/%m/%Y} — {ultima['metros']} m ({ultima['tipo']})")
