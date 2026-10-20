# Maximo-entrenamiento

App simple para registrar gimnasio y natación, con sugerencia de carga (progresión doble),
gráficos y alertas de estancamiento. Hecha con **Python + Streamlit + SQLite**.

## Instalación

Necesitás Python 3.10 o más nuevo.

```bash
# 1. Entrar a la carpeta del proyecto
cd Maximo-entrenamiento

# 2. (Recomendado) crear un entorno virtual
python -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt
```

## Ejecutar

```bash
streamlit run app.py
```

Se abre el navegador en http://localhost:8501. La base de datos se crea sola en
`datos/entrenamiento.db` la primera vez.

### Datos de ejemplo

Con la base vacía, la pantalla de **Inicio** muestra un botón para cargar datos de ejemplo.
También se puede desde la terminal:

```bash
python -m db.datos_ejemplo      # 2 semanas
python -m db.datos_ejemplo 4    # 4 semanas (así aparece la alerta de estancamiento del press militar)
```

Para empezar de cero: pantalla **Exportar → Borrar todos los datos** (o borrar el archivo `datos/entrenamiento.db`).

## Estructura

```
app.py                  Punto de entrada: arma el menú y llama a cada pantalla
requirements.txt
db/
  database.py           Todo lo que lee/escribe en SQLite (tablas y consultas)
  datos_ejemplo.py      Generador de datos de ejemplo
logica/
  rutina.py             La rutina precargada (editá acá ejercicios, series y rangos)
  progresion.py         1RM (Epley), sugerencia de carga y detección de estancamiento
  estadisticas.py       Volumen semanal y metros por semana
  exportar.py           Generación de CSV / ZIP
pantallas/
  inicio.py             Resumen y alertas
  gimnasio.py           Cargar series y ver/borrar historial
  natacion.py           Cargar sesiones de pileta
  rutina.py             Rutina con última carga y próxima sugerencia
  graficos.py           Gráficos
  exportar.py           Descargas CSV y borrar todo
datos/                  (se crea solo) la base SQLite — no se sube a git
```

La idea es: **pantallas** solo dibujan, **logica** solo calcula (no toca la base) y
**db** solo guarda/lee. Si querés cambiar una regla, casi siempre es en `logica/`.

## Cómo funciona cada cosa

**Registro de gimnasio.** Elegís fecha, día (A miércoles / B sábado; se propone solo según la fecha)
y ejercicio. Aparece una tabla con una fila por serie, ya cargada con el peso sugerido:
corregís reps, kg y RIR de cada serie, agregás notas y guardás. Se guarda una fila por serie.

**Natación.** Fecha, metros, tiempo en minutos, tipo de trabajo y esfuerzo percibido (1-10).
Los tipos se editan en `pantallas/natacion.py` (`TIPOS_DE_TRABAJO`).

**Sugerencia de carga (progresión doble)** — `logica/progresion.py`, `sugerir_carga()`.
Mira la última sesión del ejercicio:
- si hiciste todas las series, **todas** en el tope del rango y con **RIR ≥ 1** → subir
  2,5 kg (tren superior) o 5 kg (tren inferior);
- si no → mantener el peso (y te dice qué faltó).

Los incrementos están en `INCREMENTO_KG` y el RIR mínimo en `RIR_MINIMO`.
Qué ejercicio es superior/inferior se define en `logica/rutina.py` (campo `"tren"`).

**1RM estimado (Epley):** `kg × (1 + reps / 30)`, tomando la mejor serie de cada sesión.

**Volumen semanal:** suma de `reps × kg` de todas las series de la semana (lunes a domingo),
separado por día A/B. Para dominadas con peso corporal, cargá en "kg" tu peso + lastre
(o el peso del jalón) para que el volumen y el 1RM tengan sentido.

**Estancamiento:** un ejercicio está estancado si en sus **últimas 3 sesiones** el 1RM estimado
no superó el mejor 1RM que tenías **antes** de esas 3. Por eso hacen falta al menos 4 sesiones
del ejercicio (con 2 semanas de datos todavía no puede saltar). Se cambia con
`SESIONES_ESTANCAMIENTO`.

**Exportar:** descarga de gimnasio y natación en CSV, o ambos en un ZIP. Si Excel te abre
todo en una columna, cambiá `SEPARADOR` a `";"` en `logica/exportar.py`.
