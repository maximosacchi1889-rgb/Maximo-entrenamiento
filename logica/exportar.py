"""
Exportación a CSV.

Se usa codificación 'utf-8-sig' para que Excel muestre bien los acentos.
Si tu Excel abre todo en una sola columna, cambiá SEPARADOR a ";".
"""

import io
import zipfile

SEPARADOR = ","


def a_csv(df):
    """Convierte un DataFrame a CSV (en bytes, listo para descargar)."""
    tabla = df.copy()
    if "fecha" in tabla.columns:
        tabla["fecha"] = tabla["fecha"].dt.strftime("%Y-%m-%d")
    return tabla.to_csv(index=False, sep=SEPARADOR).encode("utf-8-sig")


def zip_con_todo(tablas):
    """
    Arma un .zip con un CSV por tabla.
    tablas es un diccionario {"nombre_archivo.csv": DataFrame}.
    """
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archivo_zip:
        for nombre, df in tablas.items():
            archivo_zip.writestr(nombre, a_csv(df))
    return buffer.getvalue()
