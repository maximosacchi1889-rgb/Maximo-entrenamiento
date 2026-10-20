"""
Carga datos de ejemplo para ver la app funcionando.

Uso desde la terminal (en la carpeta del proyecto):
    python -m db.datos_ejemplo          # 2 semanas (por defecto)
    python -m db.datos_ejemplo 4        # 4 semanas (con 4+ semanas aparece una alerta de estancamiento)

También se puede cargar con el botón de la pantalla de Inicio cuando la base está vacía.
Las fechas se calculan hacia atrás desde hoy, así siempre se ven "recientes".
"""

import sys
from datetime import date, timedelta

from db import database
from logica.rutina import RUTINA, DIA_DE_LA_SEMANA

# Peso inicial de cada ejercicio y reps con las que arranca.
PUNTO_DE_PARTIDA = {
    "Sentadilla trasera": (80, 5),
    "Peso muerto rumano": (70, 6),
    "Dominadas / jalón": (50, 7),
    "Press militar mancuernas": (16, 7),   # este lo dejamos "estancado" a propósito
    "Pallof press": (12, 10),
    "Remo con barra": (60, 6),
    "Press inclinado mancuernas": (22, 7),
    "Sentadilla búlgara": (16, 6),
    "Hip thrust": (90, 7),
    "Face pull": (15, 13),
}
ESTANCADO = "Press militar mancuernas"
INCREMENTO = {"superior": 2.5, "inferior": 5.0}

# Natación: martes y viernes, alternando tipos de trabajo.
NATACION = {
    1: [(1500, 35, "Técnica", 5), (1600, 36, "Técnica", 5)],              # martes
    4: [(2000, 42, "Aeróbico continuo", 6), (2200, 44, "Series / intervalos", 8)],  # viernes
}


def cargar_datos_ejemplo(semanas=2):
    """Genera `semanas` semanas de gimnasio (miércoles A / sábado B) y natación."""
    database.crear_tablas()
    hoy = date.today()
    inicio = hoy - timedelta(weeks=semanas)

    # Estado actual (kg, reps) de cada ejercicio; se va actualizando sesión a sesión.
    estado = dict(PUNTO_DE_PARTIDA)
    sesiones_hechas = {nombre: 0 for nombre in estado}
    natacion_hechas = 0

    fecha = inicio + timedelta(days=1)
    while fecha <= hoy:
        # ---- Gimnasio ----
        for dia, dia_semana in DIA_DE_LA_SEMANA.items():
            if fecha.weekday() != dia_semana:
                continue
            for ej in RUTINA[dia]:
                nombre = ej["ejercicio"]
                kg, reps = estado[nombre]

                if nombre == ESTANCADO:
                    # Siempre el mismo peso, reps que suben y bajan, RIR 0: no progresa.
                    reps = [7, 7, 6][sesiones_hechas[nombre] % 3]
                    series = [{"reps": reps, "kg": kg, "rir": 0} for _ in range(ej["series"])]
                    notas = "Me cuesta, hombro cargado"
                else:
                    # Todas las series con las mismas reps; la última con RIR 1, el resto con RIR 2.
                    series = [{"reps": reps, "kg": kg, "rir": 2} for _ in range(ej["series"])]
                    series[-1]["rir"] = 1
                    notas = ""
                    # Progresión doble: si llegó al tope, sube peso y vuelve al piso; si no, +1 rep.
                    if reps >= ej["reps_max"]:
                        estado[nombre] = (kg + INCREMENTO[ej["tren"]], ej["reps_min"])
                    else:
                        estado[nombre] = (kg, reps + 1)

                database.guardar_sesion_gym(fecha, dia, nombre, notas, series)
                sesiones_hechas[nombre] += 1

        # ---- Natación ----
        if fecha.weekday() in NATACION:
            opciones = NATACION[fecha.weekday()]
            metros, minutos, tipo, esfuerzo = opciones[natacion_hechas % len(opciones)]
            database.guardar_natacion(fecha, metros, minutos, tipo, esfuerzo)
            natacion_hechas += 1

        fecha += timedelta(days=1)


if __name__ == "__main__":
    cantidad = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    cargar_datos_ejemplo(cantidad)
    print(f"Listo: cargadas {cantidad} semanas de datos de ejemplo en {database.RUTA_DB}")
