import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import os

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

# DEFINIR EL PERIODO DE TIEMPO
hoy = datetime.now()
año_actual = hoy.year
# El rango va desde hace 10 años hasta el año actual inclusive.
años_a_extraer = range(año_actual - 10, año_actual + 1)

datos_totales = []
print("Iniciando la extracción de datos climáticos (versión final)...")

# BUCLE PRINCIPAL POR CIUDAD
for ciudad, (lat, lon) in ciudades.items():
    print(f"\nProcesando {ciudad}...")
    datos_ciudad = []

    # BUCLE INTERNO POR AÑO
    for año in años_a_extraer:
        start_date = f"{año}-01-01"

        if año == año_actual:
            # Calculamos el primer día del mes actual
            primer_dia_mes_actual = hoy.replace(day=1)
            # Restamos un día para obtener el último día del mes anterior
            end_date_dt = primer_dia_mes_actual - timedelta(days=1)
            # Formateamos la fecha a string
            end_date = end_date_dt.strftime("%Y-%m-%d")
            # Si el mes es Enero, no hay datos que extraer para el año en curso aun.
            if hoy.month == 1:
                print(f"  - Saltando año {año} (aún no hay meses completos).")
                continue
        else:
            # Para años pasados, tomamos el año completo.
            end_date = f"{año}-12-31"
            
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
                df_año = pd.DataFrame(datos_api['daily'])
                datos_ciudad.append(df_año)
            else:
                 print(f"    -> No se encontraron datos 'daily' para el período.")
            time.sleep(0.5)
        except requests.exceptions.RequestException as e:
            print(f"    -> Error al extraer el período: {e}")

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
    output_folder = 'data'
    nombre_archivo = 'datos_climaticos_chile_10_anios.csv'
    file_path = os.path.join(output_folder, nombre_archivo)

    df_final.to_csv(file_path, index=False, date_format='%Y-%m-%d')

    print("\n¡Extracción completada!")
    print(f"Se han guardado {len(df_final)} registros en el archivo '{nombre_archivo}'")
    print("\nVista previa de los datos (últimos registros):")
    print(df_final.tail())
else:
    print("\nNo se pudieron extraer datos. El archivo final no fue creado.")