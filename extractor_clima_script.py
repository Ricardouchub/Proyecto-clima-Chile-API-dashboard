import requests
import pandas as pd
from datetime import datetime
import time
import os
import calendar

# LISTA DE CAPITALES REGIONALES DE CHILE
ciudades = {
    "Arica": (-18.47, -70.31), "Iquique": (-20.21, -70.15),
    "Antofagasta": (-23.65, -70.40), "Copiapo": (-27.37, -70.33),
    "La Serena": (-29.90, -71.25), "Valparaiso": (-33.05, -71.62),
    "Santiago": (-33.46, -70.65), "Rancagua": (-34.17, -70.74),
    "Talca": (-35.43, -71.65), "Chillan": (-36.61, -72.10),
    "Concepcion": (-36.83, -73.05), "Temuco": (-38.74, -72.59),
    "Valdivia": (-39.81, -73.25), "Puerto Montt": (-41.47, -72.94),
    "Coyhaique": (-45.57, -72.07), "Punta Arenas": (-53.16, -70.92)
}


def iter_meses(inicio_anio, inicio_mes, fin_anio, fin_mes):
    anio = inicio_anio
    mes = inicio_mes
    while (anio < fin_anio) or (anio == fin_anio and mes <= fin_mes):
        yield anio, mes
        if mes == 12:
            anio += 1
            mes = 1
        else:
            mes += 1


def agrupar_rangos_meses(meses_faltantes):
    if not meses_faltantes:
        return []
    meses_ordenados = sorted(meses_faltantes)
    rangos = []
    inicio_anio, inicio_mes = meses_ordenados[0]
    prev_anio, prev_mes = inicio_anio, inicio_mes
    for anio, mes in meses_ordenados[1:]:
        prev_key = prev_anio * 12 + prev_mes
        curr_key = anio * 12 + mes
        if curr_key == prev_key + 1:
            prev_anio, prev_mes = anio, mes
            continue
        rangos.append((inicio_anio, inicio_mes, prev_anio, prev_mes))
        inicio_anio, inicio_mes = anio, mes
        prev_anio, prev_mes = anio, mes
    rangos.append((inicio_anio, inicio_mes, prev_anio, prev_mes))
    return rangos


# DEFINIR EL PERIODO DE TIEMPO
hoy = datetime.now()
anio_actual = hoy.year
anio_inicio = anio_actual - 10
if hoy.month == 1:
    anio_fin = anio_actual - 1
    mes_fin = 12
else:
    anio_fin = anio_actual
    mes_fin = hoy.month - 1

meses_objetivo = list(iter_meses(anio_inicio, 1, anio_fin, mes_fin))
sin_meses_objetivo = not meses_objetivo

output_folder = 'data'
nombre_archivo = 'datos_climaticos_chile_10_anios.csv'
file_path = os.path.join(output_folder, nombre_archivo)

df_existente = None
if os.path.exists(file_path):
    try:
        df_existente = pd.read_csv(file_path)
        if 'fecha' in df_existente.columns:
            df_existente['fecha'] = pd.to_datetime(df_existente['fecha'], errors='coerce')
        else:
            print("Archivo existente sin columna 'fecha'. Se ignorara para faltantes.")
            df_existente = None
        if df_existente is not None and 'ciudad' not in df_existente.columns:
            print("Archivo existente sin columna 'ciudad'. Se ignorara para faltantes.")
            df_existente = None
    except Exception as e:
        print(f"No se pudo leer el archivo existente: {e}")
        df_existente = None

datos_totales = []
total_meses_faltantes = 0
print("Iniciando la extraccion de datos climaticos (append)...")

if not sin_meses_objetivo:
    # BUCLE PRINCIPAL POR CIUDAD
    for ciudad, (lat, lon) in ciudades.items():
        print(f"\nProcesando {ciudad}...")
        datos_ciudad = []

        meses_existentes = set()
        if df_existente is not None:
            df_ciudad_existente = df_existente[df_existente['ciudad'] == ciudad].dropna(
                subset=['fecha']
            )
            meses_existentes = set(
                zip(df_ciudad_existente['fecha'].dt.year, df_ciudad_existente['fecha'].dt.month)
            )

        meses_faltantes = [m for m in meses_objetivo if m not in meses_existentes]
        total_meses_faltantes += len(meses_faltantes)

        if not meses_faltantes:
            print("  - No hay meses faltantes. Saltando.")
            continue

        rangos = agrupar_rangos_meses(meses_faltantes)
        for inicio_anio, inicio_mes, fin_anio, fin_mes in rangos:
            start_date = f"{inicio_anio:04d}-{inicio_mes:02d}-01"
            ultimo_dia = calendar.monthrange(fin_anio, fin_mes)[1]
            end_date = f"{fin_anio:04d}-{fin_mes:02d}-{ultimo_dia:02d}"
            print(f"  - Extrayendo: {start_date} a {end_date}...")

            url = (
                f"https://archive-api.open-meteo.com/v1/archive?"
                f"latitude={lat}&longitude={lon}&"
                f"start_date={start_date}&end_date={end_date}&"
                "daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max&"
                "timezone=auto"
            )

            try:
                response = requests.get(url, timeout=60)
                response.raise_for_status()
                datos_api = response.json()
                if 'daily' in datos_api:
                    df_rango = pd.DataFrame(datos_api['daily'])
                    datos_ciudad.append(df_rango)
                else:
                    print("    -> No se encontraron datos 'daily' para el periodo.")
                time.sleep(0.5)
            except requests.exceptions.RequestException as e:
                print(f"    -> Error al extraer el periodo: {e}")

        if datos_ciudad:
            df_ciudad_completo = pd.concat(datos_ciudad, ignore_index=True)
            df_ciudad_completo['ciudad'] = ciudad
            datos_totales.append(df_ciudad_completo)

# COMBINAR, LIMPIAR Y GUARDAR
if datos_totales:
    df_final = pd.concat(datos_totales, ignore_index=True)

    df_final.rename(columns={
        'time': 'fecha',
        'temperature_2m_max': 'temp_max_c',
        'temperature_2m_min': 'temp_min_c',
        'precipitation_sum': 'precipitacion_mm',
        'wind_speed_10m_max': 'viento_max_kmh'
    }, inplace=True)

    df_final = df_final.dropna(subset=['fecha'])
    df_final['fecha'] = pd.to_datetime(df_final['fecha'])
    df_final = df_final[['ciudad', 'fecha', 'temp_max_c', 'temp_min_c', 'precipitacion_mm', 'viento_max_kmh']]

    os.makedirs(output_folder, exist_ok=True)
    escribir_header = not os.path.exists(file_path) or os.path.getsize(file_path) == 0
    df_final.to_csv(
        file_path,
        mode='a',
        header=escribir_header,
        index=False,
        date_format='%Y-%m-%d'
    )

    print("\nExtraccion completada!")
    print(f"Se agregaron {len(df_final)} registros al archivo '{nombre_archivo}'")
    print("\nVista previa de los datos agregados (ultimos registros):")
    print(df_final.tail())
else:
    if sin_meses_objetivo:
        print("\nNo hay meses completos para extraer todavia.")
    elif total_meses_faltantes == 0:
        print("\nNo hay meses faltantes. No se agregaron datos.")
    else:
        print("\nNo se pudieron extraer datos. El archivo final no fue actualizado.")
