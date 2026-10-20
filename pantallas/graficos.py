"""Pantalla de gráficos: 1RM estimado, volumen semanal y metros nadados."""

import altair as alt
import streamlit as st

from db import database
from logica.estadisticas import metros_semanales, volumen_semanal
from logica.progresion import detectar_estancamientos, historial_1rm
from logica.rutina import RUTINA


def mostrar():
    st.title("📈 Gráficos")
    series_df = database.leer_series_gym()
    natacion_df = database.leer_natacion()

    # Alertas arriba de todo, para que se vean.
    for a in detectar_estancamientos(series_df):
        st.warning(f"⚠️ **{a['ejercicio']}**: sin progreso en las últimas 3 sesiones.")

    tab_rm, tab_volumen, tab_natacion = st.tabs(["1RM estimado", "Volumen semanal", "Natación"])

    # ---- 1RM estimado (Epley) ----
    with tab_rm:
        historial = historial_1rm(series_df)
        if historial.empty:
            st.write("Sin datos de gimnasio.")
        else:
            # Mismo orden que la rutina (+ cualquier ejercicio extra al final).
            orden = [e["ejercicio"] for dia in RUTINA.values() for e in dia]
            con_datos = set(historial["ejercicio"])
            ejercicios = [e for e in orden if e in con_datos] + sorted(con_datos - set(orden))
            elegidos = st.multiselect("Ejercicios", ejercicios, default=ejercicios[:1])
            datos = historial[historial["ejercicio"].isin(elegidos)]
            st.caption("1RM estimado = kg × (1 + reps / 30), tomando la mejor serie de cada sesión.")
            # Altair permite que el eje Y no arranque en 0 (así se nota la progresión)
            # y marcar cada sesión con un punto.
            grafico = alt.Chart(datos).mark_line(point=True).encode(
                x=alt.X("fecha:T", title="Fecha", axis=alt.Axis(format="%d/%m")),
                y=alt.Y("rm_estimado:Q", title="1RM estimado (kg)", scale=alt.Scale(zero=False)),
                color=alt.Color("ejercicio:N", title="Ejercicio"),
                tooltip=[alt.Tooltip("fecha:T", format="%d/%m/%Y"), "ejercicio", "rm_estimado"],
            )
            st.altair_chart(grafico, width="stretch")
            st.dataframe(datos, hide_index=True,
                         column_config={"fecha": st.column_config.DateColumn(format="DD/MM/YYYY")})

    # ---- Volumen semanal ----
    with tab_volumen:
        volumen = volumen_semanal(series_df)
        if volumen.empty:
            st.write("Sin datos de gimnasio.")
        else:
            st.caption("Volumen = series × reps × kg, sumado por semana (lunes a domingo).")
            st.bar_chart(volumen, x="semana", y="volumen_kg", color="dia",
                         x_label="Semana (desde el lunes)", y_label="Volumen (kg)")

    # ---- Metros nadados por semana ----
    with tab_natacion:
        metros = metros_semanales(natacion_df)
        if metros.empty:
            st.write("Sin datos de natación.")
        else:
            st.bar_chart(metros, x="semana", y="metros",
                         x_label="Semana (desde el lunes)", y_label="Metros")
