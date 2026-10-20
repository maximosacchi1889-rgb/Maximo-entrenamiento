"""
La rutina precargada.

Si querés cambiar ejercicios, series o rangos de reps, editá la lista RUTINA.
- "tren" define cuánto sube la carga sugerida: "superior" = +2,5 kg, "inferior" = +5 kg
  (los valores están en logica/progresion.py, INCREMENTO_KG).
"""

RUTINA = {
    "A": [
        {"ejercicio": "Sentadilla trasera", "series": 4, "reps_min": 5, "reps_max": 6, "tren": "inferior"},
        {"ejercicio": "Peso muerto rumano", "series": 3, "reps_min": 6, "reps_max": 8, "tren": "inferior"},
        {"ejercicio": "Dominadas / jalón", "series": 4, "reps_min": 6, "reps_max": 8, "tren": "superior"},
        {"ejercicio": "Press militar mancuernas", "series": 3, "reps_min": 6, "reps_max": 8, "tren": "superior"},
        {"ejercicio": "Pallof press", "series": 3, "reps_min": 10, "reps_max": 10, "tren": "superior"},
    ],
    "B": [
        {"ejercicio": "Remo con barra", "series": 4, "reps_min": 6, "reps_max": 8, "tren": "superior"},
        {"ejercicio": "Press inclinado mancuernas", "series": 3, "reps_min": 6, "reps_max": 8, "tren": "superior"},
        {"ejercicio": "Sentadilla búlgara", "series": 3, "reps_min": 6, "reps_max": 8, "tren": "inferior"},
        {"ejercicio": "Hip thrust", "series": 3, "reps_min": 6, "reps_max": 8, "tren": "inferior"},
        {"ejercicio": "Face pull", "series": 3, "reps_min": 12, "reps_max": 15, "tren": "superior"},
    ],
}

# Texto para mostrar en pantalla
NOMBRE_DIA = {"A": "Día A (miércoles)", "B": "Día B (sábado)"}

# Día de la semana de cada rutina (lunes=0 ... domingo=6)
DIA_DE_LA_SEMANA = {"A": 2, "B": 5}


def ejercicios_del_dia(dia):
    """Lista de nombres de ejercicios de un día ('A' o 'B')."""
    return [e["ejercicio"] for e in RUTINA[dia]]


def buscar_ejercicio(nombre):
    """Devuelve el diccionario del ejercicio (series, rango, tren) o None si no está."""
    for dia, ejercicios in RUTINA.items():
        for e in ejercicios:
            if e["ejercicio"] == nombre:
                return {**e, "dia": dia}
    return None


def esquema(ejercicio):
    """Texto tipo '4x5-6' (o '3x10' si el rango es fijo)."""
    if ejercicio["reps_min"] == ejercicio["reps_max"]:
        return f"{ejercicio['series']}x{ejercicio['reps_max']}"
    return f"{ejercicio['series']}x{ejercicio['reps_min']}-{ejercicio['reps_max']}"


def dia_sugerido(fecha):
    """Según la fecha, propone el día: sábado (o cerca del finde) = B, si no = A."""
    return "B" if fecha.weekday() >= 4 else "A"
