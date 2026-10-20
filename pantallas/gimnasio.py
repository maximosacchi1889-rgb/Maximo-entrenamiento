"""Pantalla para registrar sesiones de gimnasio y ver/borrar el historial."""

from datetime import date

import pandas as pd
import streamlit as st

from db import database
from logica.progresion import sugerir_carga
from logica.rutina import NOMBRE_DIA, buscar_ejercicio, dia_sugerido, ejercicios_del_dia, esquema


def mostrar():
    st.title("🏋️ Gimnasio")

    # Mensaje que dejamos guardado antes de recargar la pantalla (ver más abajo).
    if "mensaje_gym" in st.session_state:
        st.success(st.session_state.pop("mensaje_gym"))

    series_df = database.leer_series_gym()

    # ---------------- Formulario de carga ----------------
    st.subheader("Registrar ejercicio")
    col1, col2 = st.columns(2)
    fecha = col1.date_input("Fecha", value=date.today(), format="DD/MM/YYYY")
    # El día por defecto depende de la fecha (la key cambia con la fecha para que se actualice).
    dia = col2.radio(
        "Día", ["A", "B"],
        index=["A", "B"].index(dia_sugerido(fecha)),
        format_func=lambda d: NOMBRE_DIA[d],
        horizontal=True,
        key=f"dia_{fecha}",
    )

    nombre = st.selectbox("Ejercicio", ejercicios_del_dia(dia))
    info = buscar_ejercicio(nombre)
    sugerencia = sugerir_carga(series_df, nombre)

    st.info(f"**Objetivo:** {esquema(info)} · **Sugerencia:** {sugerencia['mensaje']}")

    # Tabla editable con una fila por serie, precargada con la sugerencia.
    kg_inicial = sugerencia["kg_sugerido"] or 0.0
    tabla_inicial = pd.DataFrame({
        "Reps": [info["reps_min"]] * info["series"],
        "Kg": [kg_inicial] * info["series"],
        "RIR": [2] * info["series"],
    })
    st.caption("Editá cada serie. Podés agregar o quitar filas (series).")
    tabla = st.data_editor(
        tabla_inicial,
        num_rows="dynamic",
        hide_index=True,
        key=f"editor_{fecha}_{nombre}",  # tabla nueva cada vez que cambia fecha/ejercicio
        column_config={
            "Reps": st.column_config.NumberColumn(min_value=0, max_value=100, step=1),
            "Kg": st.column_config.NumberColumn(min_value=0.0, max_value=500.0, step=0.5, format="%.1f"),
            "RIR": st.column_config.NumberColumn(min_value=0, max_value=10, step=1),
        },
    )
    notas = st.text_area("Notas", key=f"notas_{fecha}_{nombre}")

    if st.button("💾 Guardar", type="primary"):
        filas = tabla.dropna()  # ignoramos filas incompletas
        if filas.empty:
            st.error("Cargá al menos una serie completa.")
        else:
            lista_series = [
                {"reps": f["Reps"], "kg": f["Kg"], "rir": f["RIR"]} for _, f in filas.iterrows()
            ]
            database.guardar_sesion_gym(fecha, dia, nombre, notas, lista_series)
            st.session_state["mensaje_gym"] = f"Guardado: {nombre} ({len(lista_series)} series)."
            st.rerun()  # recargamos para que la sugerencia y el historial se actualicen

    # ---------------- Historial ----------------
    st.divider()
    st.subheader("Historial")
    if series_df.empty:
        st.write("Sin registros todavía.")
        return

    filtro = st.selectbox("Filtrar por ejercicio", ["Todos"] + sorted(series_df["ejercicio"].unique()))
    vista = series_df if filtro == "Todos" else series_df[series_df["ejercicio"] == filtro]
    vista = vista.sort_values(["fecha", "sesion_id", "serie"], ascending=[False, False, True])
    st.dataframe(
        vista,
        hide_index=True,
        column_config={"fecha": st.column_config.DateColumn("fecha", format="DD/MM/YYYY")},
    )

    # Borrar una sesión cargada por error
    with st.expander("🗑️ Borrar un registro"):
        sesiones = vista.drop_duplicates("sesion_id")
        opciones = {
            f"#{s.sesion_id} · {s.fecha:%d/%m/%Y} · {s.ejercicio}": s.sesion_id
            for s in sesiones.itertuples()
        }
        elegida = st.selectbox("Sesión", list(opciones))
        if st.button("Borrar sesión"):
            database.borrar_sesion_gym(opciones[elegida])
            st.session_state["mensaje_gym"] = f"Borrada: {elegida}"
            st.rerun()
