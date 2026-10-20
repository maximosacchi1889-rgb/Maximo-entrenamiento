"""
Cálculos de progresión: 1RM estimado, sugerencia de carga y estancamiento.

Todas las funciones reciben el DataFrame que devuelve db.database.leer_series_gym()
(una fila por serie) y no tocan la base de datos.
"""

from logica.rutina import buscar_ejercicio

# Cuánto subir la carga cuando se cumple la progresión doble.
INCREMENTO_KG = {"superior": 2.5, "inferior": 5.0}

# RIR mínimo en todas las series para considerar que la carga "sobró".
RIR_MINIMO = 1

# Cantidad de sesiones seguidas sin mejorar para disparar la alerta.
SESIONES_ESTANCAMIENTO = 3


def rm_epley(kg, reps):
    """1RM estimado con la fórmula de Epley: kg x (1 + reps / 30)."""
    return kg * (1 + reps / 30)


def ultima_sesion(series_df, ejercicio):
    """Devuelve las series de la última sesión registrada de un ejercicio (o None)."""
    del_ejercicio = series_df[series_df["ejercicio"] == ejercicio]
    if del_ejercicio.empty:
        return None
    # La última sesión es la de fecha más reciente (y, si hay empate, la última cargada).
    ultima = del_ejercicio.sort_values(["fecha", "sesion_id"]).iloc[-1]
    return del_ejercicio[del_ejercicio["sesion_id"] == ultima["sesion_id"]]


def sugerir_carga(series_df, ejercicio):
    """
    Progresión doble:
      - Si en la última sesión hiciste TODAS las series pedidas, todas en el tope del
        rango de reps y con RIR >= 1  -> subir 2,5 kg (tren superior) o 5 kg (inferior).
      - Si no -> mantener el peso y buscar más reps.

    Devuelve un diccionario con:
      accion       -> "subir", "mantener" o "sin_datos"
      kg_actual    -> peso usado la última vez (el más alto de las series)
      kg_sugerido  -> peso a usar la próxima
      mensaje      -> texto para mostrar
    """
    info = buscar_ejercicio(ejercicio)
    sesion = ultima_sesion(series_df, ejercicio)

    if info is None or sesion is None:
        return {"accion": "sin_datos", "kg_actual": None, "kg_sugerido": None,
                "mensaje": "Sin registros previos: elegí un peso con el que llegues al rango con RIR 1-2."}

    kg_actual = float(sesion["kg"].max())

    hizo_todas_las_series = len(sesion) >= info["series"]
    todas_en_el_tope = (sesion["reps"] >= info["reps_max"]).all()
    rir_suficiente = (sesion["rir"] >= RIR_MINIMO).all()

    if hizo_todas_las_series and todas_en_el_tope and rir_suficiente:
        incremento = INCREMENTO_KG[info["tren"]]
        kg_nuevo = kg_actual + incremento
        return {"accion": "subir", "kg_actual": kg_actual, "kg_sugerido": kg_nuevo,
                "mensaje": f"⬆️ Subí a {kg_nuevo:g} kg (+{incremento:g} kg) y volvé al piso del rango."}

    # Explicamos por qué no se sube, así sabés qué te falta.
    motivos = []
    if not hizo_todas_las_series:
        motivos.append(f"faltaron series ({len(sesion)}/{info['series']})")
    if not todas_en_el_tope:
        motivos.append(f"no todas llegaron a {info['reps_max']} reps")
    if not rir_suficiente:
        motivos.append(f"alguna serie con RIR < {RIR_MINIMO}")
    return {"accion": "mantener", "kg_actual": kg_actual, "kg_sugerido": kg_actual,
            "mensaje": f"➡️ Mantené {kg_actual:g} kg ({', '.join(motivos)})."}


def historial_1rm(series_df):
    """
    1RM estimado por sesión: para cada sesión toma la MEJOR serie (la de mayor 1RM).
    Devuelve columnas: sesion_id, fecha, ejercicio, rm_estimado
    """
    if series_df.empty:
        return series_df.assign(rm_estimado=[])[["sesion_id", "fecha", "ejercicio", "rm_estimado"]]
    df = series_df.copy()
    df["rm_estimado"] = rm_epley(df["kg"], df["reps"])
    por_sesion = (
        df.groupby(["sesion_id", "fecha", "ejercicio"], as_index=False)["rm_estimado"].max()
        .sort_values(["fecha", "sesion_id"])
    )
    por_sesion["rm_estimado"] = por_sesion["rm_estimado"].round(1)
    return por_sesion


def detectar_estancamientos(series_df):
    """
    Un ejercicio está estancado si en sus últimas 3 sesiones el 1RM estimado
    NO superó el mejor 1RM que tenías antes de esas 3 sesiones.
    (Hacen falta al menos 4 sesiones del ejercicio para poder evaluarlo.)

    Devuelve una lista de diccionarios: ejercicio, mejor_previo, mejor_reciente.
    """
    alertas = []
    historial = historial_1rm(series_df)
    for ejercicio, grupo in historial.groupby("ejercicio"):
        valores = grupo["rm_estimado"].tolist()
        if len(valores) <= SESIONES_ESTANCAMIENTO:
            continue  # pocos datos todavía
        previas = valores[:-SESIONES_ESTANCAMIENTO]
        recientes = valores[-SESIONES_ESTANCAMIENTO:]
        if max(recientes) <= max(previas):
            alertas.append({
                "ejercicio": ejercicio,
                "mejor_previo": max(previas),
                "mejor_reciente": max(recientes),
            })
    return alertas
