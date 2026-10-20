"""Pantalla que muestra la rutina con la última carga y la sugerencia de cada ejercicio."""

import pandas as pd
import streamlit as st

from db import database
from logica.progresion import sugerir_carga, ultima_sesion
from logica.rutina import NOMBRE_DIA, RUTINA, esquema


def mostrar():
    st.title("📋 Rutina")
    st.caption(
        "Progresión doble: cuando todas las series llegan al tope del rango con RIR ≥ 1, "
        "se sube 2,5 kg (tren superior) o 5 kg (tren inferior)."
    )
    series_df = database.leer_series_gym()

    for dia, ejercicios in RUTINA.items():
        st.subheader(NOMBRE_DIA[dia])
        filas = []
        for ej in ejercicios:
            sesion = ultima_sesion(series_df, ej["ejercicio"])
            if sesion is None:
                ultimo = "—"
            else:
                reps = "/".join(str(r) for r in sesion["reps"])
                ultimo = f"{sesion['kg'].max():g} kg × {reps} ({sesion['fecha'].iloc[0]:%d/%m})"
            filas.append({
                "Ejercicio": ej["ejercicio"],
                "Esquema": esquema(ej),
                "Tren": ej["tren"],
                "Última vez": ultimo,
                "Próxima": sugerir_carga(series_df, ej["ejercicio"])["mensaje"],
            })
        st.dataframe(pd.DataFrame(filas), hide_index=True, width="stretch")
