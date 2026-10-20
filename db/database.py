"""
Acceso a la base de datos SQLite.

Todo lo que lee o escribe en la base pasa por este archivo. Así, si algún día
querés cambiar SQLite por otra cosa, solo tocás acá.

Tablas:
    sesiones_gym  -> una fila por ejercicio hecho en un día (fecha, día A/B, ejercicio, notas)
    series        -> una fila por serie de esa sesión (reps, kg, RIR)
    natacion      -> una fila por sesión de pileta
"""

import sqlite3
from pathlib import Path

import pandas as pd

# La base se guarda en la carpeta "datos/" en la raíz del proyecto.
RUTA_DB = Path(__file__).resolve().parent.parent / "datos" / "entrenamiento.db"


def conectar():
    """Abre una conexión a la base (y crea la carpeta si no existe)."""
    RUTA_DB.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(RUTA_DB)
    # Necesario para que al borrar una sesión se borren también sus series.
    con.execute("PRAGMA foreign_keys = ON")
    return con


def crear_tablas():
    """Crea las tablas si todavía no existen. Se llama al arrancar la app."""
    con = conectar()
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS sesiones_gym (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha     TEXT NOT NULL,          -- formato AAAA-MM-DD
            dia       TEXT NOT NULL,          -- 'A' o 'B'
            ejercicio TEXT NOT NULL,
            notas     TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS series (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            sesion_id INTEGER NOT NULL REFERENCES sesiones_gym(id) ON DELETE CASCADE,
            numero    INTEGER NOT NULL,       -- 1, 2, 3...
            reps      INTEGER NOT NULL,
            kg        REAL NOT NULL,
            rir       INTEGER NOT NULL        -- repeticiones en reserva
        );

        CREATE TABLE IF NOT EXISTS natacion (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha      TEXT NOT NULL,
            metros     INTEGER NOT NULL,
            tiempo_min REAL NOT NULL,         -- duración en minutos
            tipo       TEXT NOT NULL,         -- técnica, aeróbico, series...
            esfuerzo   INTEGER NOT NULL       -- esfuerzo percibido 1-10
        );
        """
    )
    con.commit()
    con.close()


# ---------------------------------------------------------------------------
# Gimnasio
# ---------------------------------------------------------------------------

def guardar_sesion_gym(fecha, dia, ejercicio, notas, lista_series):
    """
    Guarda un ejercicio hecho en una fecha, con todas sus series.

    lista_series es una lista de diccionarios, por ejemplo:
        [{"reps": 6, "kg": 80, "rir": 2}, {"reps": 6, "kg": 80, "rir": 1}]
    Devuelve el id de la sesión creada.
    """
    con = conectar()
    cursor = con.execute(
        "INSERT INTO sesiones_gym (fecha, dia, ejercicio, notas) VALUES (?, ?, ?, ?)",
        (str(fecha), dia, ejercicio, notas),
    )
    sesion_id = cursor.lastrowid
    for numero, s in enumerate(lista_series, start=1):
        con.execute(
            "INSERT INTO series (sesion_id, numero, reps, kg, rir) VALUES (?, ?, ?, ?, ?)",
            (sesion_id, numero, int(s["reps"]), float(s["kg"]), int(s["rir"])),
        )
    con.commit()
    con.close()
    return sesion_id


def leer_series_gym():
    """
    Devuelve TODAS las series de gimnasio en una tabla (DataFrame de pandas),
    una fila por serie, con los datos de su sesión al lado.
    Columnas: sesion_id, fecha, dia, ejercicio, serie, reps, kg, rir, notas
    """
    con = conectar()
    df = pd.read_sql_query(
        """
        SELECT s.id AS sesion_id, s.fecha, s.dia, s.ejercicio,
               se.numero AS serie, se.reps, se.kg, se.rir, s.notas
        FROM sesiones_gym s
        JOIN series se ON se.sesion_id = s.id
        ORDER BY s.fecha, s.id, se.numero
        """,
        con,
        parse_dates=["fecha"],
    )
    con.close()
    return df


def borrar_sesion_gym(sesion_id):
    """Borra una sesión de gimnasio (y sus series, por el ON DELETE CASCADE)."""
    con = conectar()
    con.execute("DELETE FROM sesiones_gym WHERE id = ?", (int(sesion_id),))
    con.commit()
    con.close()


# ---------------------------------------------------------------------------
# Natación
# ---------------------------------------------------------------------------

def guardar_natacion(fecha, metros, tiempo_min, tipo, esfuerzo):
    """Guarda una sesión de natación."""
    con = conectar()
    con.execute(
        "INSERT INTO natacion (fecha, metros, tiempo_min, tipo, esfuerzo) VALUES (?, ?, ?, ?, ?)",
        (str(fecha), int(metros), float(tiempo_min), tipo, int(esfuerzo)),
    )
    con.commit()
    con.close()


def leer_natacion():
    """Devuelve todas las sesiones de natación ordenadas por fecha."""
    con = conectar()
    df = pd.read_sql_query(
        "SELECT * FROM natacion ORDER BY fecha, id", con, parse_dates=["fecha"]
    )
    con.close()
    return df


def borrar_natacion(natacion_id):
    """Borra una sesión de natación."""
    con = conectar()
    con.execute("DELETE FROM natacion WHERE id = ?", (int(natacion_id),))
    con.commit()
    con.close()


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def base_vacia():
    """True si no hay ningún registro cargado todavía."""
    con = conectar()
    n_gym = con.execute("SELECT COUNT(*) FROM sesiones_gym").fetchone()[0]
    n_nat = con.execute("SELECT COUNT(*) FROM natacion").fetchone()[0]
    con.close()
    return n_gym == 0 and n_nat == 0


def borrar_todo():
    """Vacía todas las tablas (¡cuidado!)."""
    con = conectar()
    con.execute("DELETE FROM series")
    con.execute("DELETE FROM sesiones_gym")
    con.execute("DELETE FROM natacion")
    con.commit()
    con.close()
