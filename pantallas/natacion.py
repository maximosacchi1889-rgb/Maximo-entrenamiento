"""Pantalla para registrar sesiones de natación."""

from datetime import date

import streamlit as st

from db import database

# Tipos de trabajo disponibles. Agregá o quitá los que quieras.
TIPOS_DE_TRABAJO = [
    "Técnica",
    "Aeróbico continuo",
    "Series / intervalos",
    "Velocidad",
    "Recuperación",
]


def mostrar():
    st.title("🏊 Natación")

    if "mensaje_nat" in st.session_state:
        st.success(st.session_state.pop("mensaje_nat"))

    # st.form agrupa los campos: la app recién se actualiza al apretar "Guardar".
    with st.form("form_natacion", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        fecha = col1.date_input("Fecha", value=date.today(), format="DD/MM/YYYY")
        metros = col2.number_input("Metros", min_value=0, max_value=20000, value=1500, step=50)
        tiempo = col3.number_input("Tiempo (minutos)", min_value=0.0, max_value=600.0, value=35.0, step=1.0)
        tipo = st.selectbox("Tipo de trabajo", TIPOS_DE_TRABAJO)
        esfuerzo = st.slider("Esfuerzo percibido (1 = muy suave, 10 = máximo)", 1, 10, 6)
        guardar = st.form_submit_button("💾 Guardar", type="primary")

    if guardar:
        if metros <= 0 or tiempo <= 0:
            st.error("Metros y tiempo tienen que ser mayores a cero.")
        else:
            database.guardar_natacion(fecha, metros, tiempo, tipo, esfuerzo)
            st.session_state["mensaje_nat"] = f"Guardado: {metros} m en {tiempo:g} min."
            st.rerun()

    # ---------------- Historial ----------------
    st.divider()
    st.subheader("Historial")
    df = database.leer_natacion()
    if df.empty:
        st.write("Sin registros todavía.")
        return

    # Ritmo cada 100 m (minutos), calculado al vuelo para mostrar.
    df["min_por_100m"] = (df["tiempo_min"] / df["metros"] * 100).round(2)
    df = df.sort_values("fecha", ascending=False)
    st.dataframe(
        df,
        hide_index=True,
        column_config={"fecha": st.column_config.DateColumn("fecha", format="DD/MM/YYYY")},
    )

    with st.expander("🗑️ Borrar un registro"):
        opciones = {f"#{r.id} · {r.fecha:%d/%m/%Y} · {r.metros} m": r.id for r in df.itertuples()}
        elegida = st.selectbox("Sesión", list(opciones))
        if st.button("Borrar sesión"):
            database.borrar_natacion(opciones[elegida])
            st.session_state["mensaje_nat"] = f"Borrada: {elegida}"
            st.rerun()
