"""Pantalla para descargar los datos en CSV (y borrar todo si hace falta)."""

from datetime import date

import streamlit as st

from db import database
from logica.exportar import a_csv, zip_con_todo


def mostrar():
    st.title("💾 Exportar")
    series_df = database.leer_series_gym()
    natacion_df = database.leer_natacion()
    hoy = date.today().isoformat()

    st.write(f"Gimnasio: **{len(series_df)}** series · Natación: **{len(natacion_df)}** sesiones.")

    col1, col2, col3 = st.columns(3)
    col1.download_button("Gimnasio (CSV)", a_csv(series_df),
                         file_name=f"gimnasio_{hoy}.csv", mime="text/csv")
    col2.download_button("Natación (CSV)", a_csv(natacion_df),
                         file_name=f"natacion_{hoy}.csv", mime="text/csv")
    col3.download_button(
        "Todo (ZIP con ambos CSV)",
        zip_con_todo({"gimnasio.csv": series_df, "natacion.csv": natacion_df}),
        file_name=f"entrenamiento_{hoy}.zip",
        mime="application/zip",
        type="primary",
    )

    # Zona peligrosa: útil para sacar los datos de ejemplo y empezar de cero.
    st.divider()
    with st.expander("⚠️ Borrar todos los datos"):
        st.write("Esto borra TODO lo cargado. Exportá antes si querés guardar una copia.")
        confirmar = st.checkbox("Sí, quiero borrar todo")
        if st.button("Borrar todo", disabled=not confirmar):
            database.borrar_todo()
            st.success("Base vaciada.")
            st.rerun()
