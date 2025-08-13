# Análisis de los útimos 10 años del Clima en Chile con Dashboard


<p align="left">
  <img src="https://img.shields.io/badge/Proyecto_Completado-%E2%9C%94-2ECC71?style=flat-square&logo=checkmarx&logoColor=white" alt="Proyecto Completado"/>
  <img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Open_Meteo-API_Clima-FF6C37?style=flat-square&logo=openweathermap&logoColor=white" alt="OpenWeatherMap"/>
  <img src="https://img.shields.io/badge/Plotly-Visualización_Interactiva-3F4F75?style=flat-square&logo=plotly&logoColor=white" alt="Plotly"/>
    <img src="https://img.shields.io/badge/Gunicorn-Servidor_Web-499848?style=flat-square&logo=gunicorn&logoColor=white" alt="Gunicorn"/>
  <img src="https://img.shields.io/badge/Render-Cloud_Hosting-46E3B7?style=flat-square&logo=render&logoColor=white" alt="Render"/>
</p>

Análisis de 10 años de datos meteorológicos de las 16 capitales regionales de Chile, desde la extracción de datos vía API hasta un dashboard interactivo.

### [Notebook](https://github.com/Ricardouchub/Proyecto-clima-Chile-API-dashboard/blob/main/Notebook.ipynb)

### [Dashboard](https://proyecto-clima-chile-api-dashboard.onrender.com)

<img width="749" height="379" alt="image" src="https://github.com/user-attachments/assets/17512aa5-2169-42b6-bb71-68b84d198148" />


---

## **Índice**
1. [Descripción del Proyecto](#1-descripción-del-proyecto)
2. [Fuente de Datos](#2-fuente-de-datos)
3. [Fases del PRoyecto](#3-fases-del-proyecto)
4. [Conclusiones](#4-conclusiones)
5. [Herramientas](#5-herramientas)
6. [Autor](#6-autor)

---

## **1. Descripción del Proyecto**
El objetivo de este proyecto es realizar un ciclo completo de vida de datos, transformando información meteorológica cruda en una herramienta de visualización interactiva y accesible. El análisis se enfoca en dos áreas:

* Exploratorio: Investigar y comparar las características climáticas de las capitales de Chile para entender patrones, tendencias y eventos extremos a lo largo de la última década.

* Aplicado: Construir y desplegar una aplicación web que permita a los usuarios explorar dinámicamente los datos de temperatura, precipitación y viento, facilitando la comprensión del comportamiento climático del país.

## **2. Fuente de Datos**
Se creó un script `extractor_clima_script.py` para extraer los datos de una API pública y gratuita de **Open-Meteo**, que proporciona datos meteorológicos históricos y de pronóstico de alta calidad. Se consultó el endpoint de Archivo Histórico para obtener las siguientes variables diarias para cada una de las 16 capitales regionales de Chile desde 2015 hasta 2025:

* Temperatura máxima `temperature_2m_max`

* Temperatura mínima `temperature_2m_min`

* Suma de precipitaciones `precipitation_sum`

* Velocidad máxima del viento `wind_speed_10m_max`

## **3. Fases del Proyecto**

* **Fase 1: Extracción de Datos**
Se desarrolló un script en Python para automatizar la recolección de datos. Este script realiza peticiones a la API de Open-Meteo para cada ciudad, manejando la paginación por año para evitar errores de timeout. Los datos extraídos fueron consolidados y guardados en un único archivo CSV limpio.

* **Fase 2: Análisis Exploratorio de Datos (EDA)**
Se realizó un análisis profundo para:

    Visualizar la distribución y variabilidad de las métricas climáticas por ciudad.

    Identificar y comparar los patrones estacionales.

    Analizar tendencias a largo plazo en la temperatura.

    Detectar y cuantificar eventos extremos como olas de calor.

* **Fase 3: Dashboard Interactivo**
Se construyó una aplicación web con Dash y Plotly Express. El dashboard fue diseñado con un enfoque en la usabilidad y la estética, utilizando Dash Bootstrap Components para un layout moderno y responsive. Incluye:

    Filtros dinámicos por ciudad, métrica y un selector de rango de fechas mejorado.

    Tarjetas de KPIs que resumen los datos seleccionados.

Gráficos interactivos, incluyendo series de tiempo, mapas, análisis de anomalías y boxplots.

* **Fase 4: Despliegue del dashboard**
La aplicación final fue preparada para producción utilizando un servidor web Gunicorn. Se configuraron los archivos Procfile y requirements.txt, y el proyecto fue subido a un repositorio de GitHub. Finalmente, se desplegó en la plataforma Render, haciendo el dashboard accesible públicamente.

## **4. Conclusiones**
El análisis reveló insights clave sobre el clima de Chile:

* Se visualiza claramente la transición desde un clima desértico estable y cálido en el norte (Arica, Iquique) hacia climas templados con alta estacionalidad en el centro (Santiago) y climas fríos y ventosos en el sur (Punta Arenas).

* El análisis de anomalías mensuales permitió identificar veranos e inviernos que fueron significativamente más cálidos o fríos que el promedio histórico de 10 años para cada ciudad.

* Se observó que las ciudades de los valles centrales son más propensas a experimentar olas de calor (múltiples días consecutivos sobre el percentil 95 de temperatura) en comparación con las ciudades costeras.

## **5. Herramientas**
`Python 3.9`

`Pandas` y `NumPy` para la manipulación y análisis de datos.

`Requests` para la interacción con la API.

`Matplotlib` y `Seaborn` para la visualización de datos en el EDA.

`Dash`, `Plotly Express` y `Dash Bootstrap Components` para la construcción del dashboard.

`Gunicorn` como servidor web.

`Render` para el hosting en la nube.

## **6. Autor**
**Ricardo Urdaneta**

[**LinkedIn**](https://www.linkedin.com/in/ricardourdanetacastro/)
