"""
Resúmenes semanales para los gráficos.

Las semanas empiezan el lunes. La columna "semana" es un texto 'AAAA-MM-DD'
con la fecha de ese lunes (así se ordena bien en los gráficos).
"""

import pandas as pd


def _lunes_de_la_semana(fechas):
    """Convierte cada fecha al lunes de su semana, como texto AAAA-MM-DD."""
    return (fechas - pd.to_timedelta(fechas.dt.weekday, unit="D")).dt.strftime("%Y-%m-%d")


def volumen_semanal(series_df):
    """
    Volumen = series x reps x kg. Como cada fila ya es UNA serie, alcanza con
    sumar reps x kg de todas las filas de la semana.
    Devuelve columnas: semana, dia, volumen_kg  (separado por día A/B)
    """
    if series_df.empty:
        return pd.DataFrame(columns=["semana", "dia", "volumen_kg"])
    df = series_df.copy()
    df["volumen_kg"] = df["reps"] * df["kg"]
    df["semana"] = _lunes_de_la_semana(df["fecha"])
    return df.groupby(["semana", "dia"], as_index=False)["volumen_kg"].sum()


def metros_semanales(natacion_df):
    """Suma de metros nadados por semana. Columnas: semana, metros"""
    if natacion_df.empty:
        return pd.DataFrame(columns=["semana", "metros"])
    df = natacion_df.copy()
    df["semana"] = _lunes_de_la_semana(df["fecha"])
    return df.groupby("semana", as_index=False)["metros"].sum()
