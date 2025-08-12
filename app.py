# dash_app_moderno.py
# Versión final y refinada del Dashboard Climático de Chile
# - Diseño responsive con barra lateral más angosta
# - Estilos CSS personalizados para controles
# - Panel de instrucciones y título actualizado
# - Selector de fecha mejorado

import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime
import calendar

# --------------------
# 1) CARGA DE DATOS
# --------------------
DF_PATH = 'datos_climaticos_chile_10_anios.csv'

try:
    df = pd.read_csv(DF_PATH)
except Exception as e:
    raise FileNotFoundError(f"No se pudo leer {DF_PATH}: {e}")

# Normalizar fechas y columnas
df['fecha'] = pd.to_datetime(df['fecha'])
df['mes'] = df['fecha'].dt.month
df['año'] = df['fecha'].dt.year

# Coordenadas
coordenadas = {
    "Arica": (-18.47, -70.31), "Iquique": (-20.21, -70.15),
    "Antofagasta": (-23.65, -70.40), "Copiapo": (-27.37, -70.33),
    "La Serena": (-29.90, -71.25), "Valparaiso": (-33.05, -71.62),
    "Santiago": (-33.46, -70.65), "Rancagua": (-34.17, -70.74),
    "Talca": (-35.43, -71.65), "Chillan": (-36.61, -72.10),
    "Concepcion": (-36.83, -73.05), "Temuco": (-38.74, -72.59),
    "Valdivia": (-39.81, -73.25), "Puerto Montt": (-41.47, -72.94),
    "Coyhaique": (-45.57, -72.07), "Punta Arenas": (-53.16, -70.92)
}

df_coords = pd.DataFrame(coordenadas.items(), columns=['ciudad', 'coords'])
df_coords[['lat', 'lon']] = pd.DataFrame(df_coords['coords'].tolist(), index=df_coords.index)
if 'ciudad' not in df.columns:
    raise KeyError('El dataframe debe contener la columna "ciudad"')
df = pd.merge(df, df_coords[['ciudad', 'lat', 'lon']], on='ciudad', how='left')

# Controles
ciudades_disponibles = sorted(df['ciudad'].unique())
metricas_disponibles = {
    'temp_max_c': 'Temperatura Máxima (°C)',
    'precipitacion_mm': 'Precipitación (mm)',
    'viento_max_kmh': 'Velocidad del Viento (km/h)'
}
available_years = sorted(df['año'].unique())
month_options = [
    {'label': 'Enero', 'value': 1}, {'label': 'Febrero', 'value': 2},
    {'label': 'Marzo', 'value': 3}, {'label': 'Abril', 'value': 4},
    {'label': 'Mayo', 'value': 5}, {'label': 'Junio', 'value': 6},
    {'label': 'Julio', 'value': 7}, {'label': 'Agosto', 'value': 8},
    {'label': 'Septiembre', 'value': 9}, {'label': 'Octubre', 'value': 10},
    {'label': 'Noviembre', 'value': 11}, {'label': 'Diciembre', 'value': 12}
]

# --------------------
# 2) APP (estilos y tema)
# --------------------
external_stylesheets = [dbc.themes.DARKLY, dbc.icons.FONT_AWESOME]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, title='Dashboard Clima Chile')
server = app.server

# CSS personalizado
app.index_string = app.index_string.replace(
    '<head>',
    '<head>\n    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">\n    <style>\n        body { font-family: "Inter", system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial; }\n        .sidebar { min-height: 100vh; padding: 1.25rem; }\n        .kpi-card { border-radius: 12px; box-shadow: 0 6px 18px rgba(2,6,23,0.6); background-color: #2c2c2c; }\n        .muted { color: rgba(255,255,255,0.65); }\n        .small { font-size: 0.85rem; }\n        .brand { letter-spacing: 0.6px; font-weight:700; }\n        /* Estilos para los dropdowns */ \n        .dropdown-fix .Select-control { background-color: #222 !important; border: 1px solid #444; } \n        .dropdown-fix .Select-input > input { color: white !important; } \n        .dropdown-fix .Select-menu-outer { background-color: #333 !important; border: 1px solid #555; } \n        .dropdown-fix .Select-option { color: #f0f0f0 !important; background-color: #333; } \n        .dropdown-fix .Select-option.is-focused { background-color: #0d6efd !important; color: white !important; } \n        .dropdown-fix .Select--multi .Select-value { color: white !important; background-color: #0d6efd !important; border-radius: 4px; } \n        .dropdown-fix .Select-placeholder, .dropdown-fix .Select--single > .Select-control .Select-value { color: #ccc !important; } \n    </style>'
)

# --------------------
# 3) LAYOUT
# --------------------

sidebar = html.Div([
    html.Div([
        html.H2('Dashboard Clima de Chile (2015-2025)', className='brand text-light'),
        html.P('Análisis interactivo de datos', className='muted small'),
    ], className='mb-4'),

    dbc.Card(
        dbc.CardBody([
            html.H6("Instrucciones", className="card-title text-white"),
            html.P("Usa los filtros y presiona 'Actualizar' para explorar los datos.", className="small muted")
        ]),
        color="dark",
        className="mb-4"
    ),

    html.Label('Ciudades', className='text-light small'),
    dcc.Dropdown(id='selector-ciudad', options=[{'label': c, 'value': c} for c in ciudades_disponibles], value=['Santiago', 'Valparaiso'], multi=True, placeholder='Selecciona ciudades...', className='dropdown-fix'),
    html.Br(),

    html.Label('Métrica', className='text-light small'),
    dbc.RadioItems(id='selector-metrica', options=[{'label': v, 'value': k} for k, v in metricas_disponibles.items()], value='temp_max_c', inline=False),
    html.Br(),

    # --- ¡NUEVO! Selector de fecha mejorado ---
    html.Label('Rango de Fechas', className='text-light small mb-2'),
    dbc.Card(
        dbc.CardBody([
            html.Div("Desde:", className="small muted"),
            dbc.Row([
                dbc.Col(dcc.Dropdown(id='selector-año-inicio', options=[{'label': y, 'value': y} for y in available_years], value=available_years[-2], placeholder="Año", className='dropdown-fix'), width=6),
                dbc.Col(dcc.Dropdown(id='selector-mes-inicio', options=month_options, value=df['fecha'].max().month, placeholder="Mes", className='dropdown-fix'), width=6),
            ], className="mb-2"),
            html.Div("Hasta:", className="small muted"),
            dbc.Row([
                dbc.Col(dcc.Dropdown(id='selector-año-fin', options=[{'label': y, 'value': y} for y in available_years], value=available_years[-1], placeholder="Año", className='dropdown-fix'), width=6),
                dbc.Col(dcc.Dropdown(id='selector-mes-fin', options=month_options, value=df['fecha'].max().month, placeholder="Mes", className='dropdown-fix'), width=6),
            ]),
        ]),
        color="dark",
        className="mb-3"
    ),

    dbc.Button('Actualizar', id='btn-actualizar', color='primary', className='mb-3 w-100', n_clicks=0),

    html.Hr(),
    html.P('Opciones', className='text-light small'),
    dbc.Checklist(options=[{'label': 'Mostrar medias móviles (7d)', 'value': 'ma7'}, {'label': 'Suavizar líneas', 'value': 'smooth'}], value=['ma7'], id='opciones-graficos', inline=False),
    html.Div(id='version-info', className='muted small mt-4', children=[f'Última actualización: {datetime.now().strftime("%Y-%m-%d")}']),
    
    html.Div([
        html.Hr(),
        html.P("Realizado por: Ricardo Urdaneta", className="small text-white"),
        html.Div([
            html.A(dbc.Button(html.I(className="fab fa-github"), color="light", outline=True, size="sm"), href="https://github.com/Ricardouchub", target="_blank", className="me-2"),
            html.A(dbc.Button(html.I(className="fab fa-linkedin"), color="light", outline=True, size="sm"), href="https://www.linkedin.com/in/ricardourdanetacastro/", target="_blank"),
        ])
    ], className="text-center mt-4")

], className='sidebar')

content = html.Div([
    html.Div(id='fila-kpis', className='mb-4'),
    dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody([html.H6('Serie de Tiempo', className='card-title'), dcc.Loading(dcc.Graph(id='grafico-serie-tiempo'), type='default')] ), className='kpi-card'), width=7),
        dbc.Col(dbc.Card(dbc.CardBody([html.H6('Mapa Interactivo', className='card-title'), dcc.Loading(dcc.Graph(id='mapa-interactivo'), type='default')] ), className='kpi-card'), width=5),
    ], className='mb-4'),
    dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody([html.H6('Anomalías Mensuales', className='card-title'), dcc.Loading(dcc.Graph(id='grafico-anomalias'), type='default')] ), className='kpi-card'), width=7),
        dbc.Col(dbc.Card(dbc.CardBody([html.H6('Distribución por Ciudad', className='card-title'), dcc.Loading(dcc.Graph(id='grafico-distribucion'), type='default')] ), className='kpi-card'), width=5),
    ], className='mb-4'),
    dcc.Store(id='df-filtrado'),
])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(sidebar, width=12, lg=2),
        dbc.Col(content, width=12, lg=10, style={'padding': '2rem'})
    ], className="g-0")
], fluid=True, className="p-0")


# --------------------
# 4) HELPERS
# --------------------
def filtrar_dataframe(ciudades, start_date, end_date):
    df_local = df.copy()
    if ciudades:
        df_local = df_local[df_local['ciudad'].isin(ciudades)]
    if start_date:
        df_local = df_local[df_local['fecha'] >= pd.to_datetime(start_date)]
    if end_date:
        df_local = df_local[df_local['fecha'] <= pd.to_datetime(end_date)]
    return df_local

# --------------------
# 5) CALLBACKS
# --------------------
@app.callback(
    Output('df-filtrado', 'data'),
    [Input('btn-actualizar', 'n_clicks')],
    # --- ¡NUEVO! Se usan los nuevos selectores de fecha como State ---
    [State('selector-ciudad', 'value'),
     State('selector-año-inicio', 'value'),
     State('selector-mes-inicio', 'value'),
     State('selector-año-fin', 'value'),
     State('selector-mes-fin', 'value')]
)
def actualizar_store(n_clicks, ciudades, año_inicio, mes_inicio, año_fin, mes_fin):
    # Maneja el caso donde los selectores no tienen valor inicial
    if not all([año_inicio, mes_inicio, año_fin, mes_fin]):
        return pd.DataFrame().to_json(date_format='iso', orient='records')

    # Construye las fechas de inicio y fin
    start_date = f"{año_inicio}-{mes_inicio:02d}-01"
    _, last_day = calendar.monthrange(año_fin, mes_fin)
    end_date = f"{año_fin}-{mes_fin:02d}-{last_day}"
    
    df_local = filtrar_dataframe(ciudades, start_date, end_date)
    return df_local.to_json(date_format='iso', orient='records')

@app.callback(
    [Output('fila-kpis', 'children'), Output('grafico-serie-tiempo', 'figure'), Output('mapa-interactivo', 'figure'), Output('grafico-anomalias', 'figure'), Output('grafico-distribucion', 'figure')],
    [Input('df-filtrado', 'data'), Input('selector-metrica', 'value'), Input('opciones-graficos', 'value')]
)
def renderizar_dashboard(df_json, metrica, opciones):
    if not df_json:
        return [], go.Figure(), go.Figure(), go.Figure(), go.Figure()

    df_filtrado = pd.read_json(df_json, convert_dates=['fecha'])
    if df_filtrado.empty:
        return [], go.Figure(), go.Figure(), go.Figure(), go.Figure()

    # KPIs
    prom = df_filtrado[metrica].mean()
    ult = df_filtrado.sort_values('fecha').iloc[-1][metrica]
    primero = df_filtrado.sort_values('fecha').iloc[0][metrica]
    cambio_pct = (ult - primero) / (abs(primero) + 1e-9) * 100

    def kpi_card(titulo, valor, sub, icon='fas fa-thermometer-half'):
        return dbc.Col(dbc.Card(dbc.CardBody([
            html.Div([html.I(className=icon + ' fa-2x'), html.Span(titulo, className='ms-3 muted small')], className='d-flex align-items-center'),
            html.H3(f"{valor:.2f}"),
            html.P(sub, className='muted small')
        ]), className='kpi-card p-3'), md=4)

    kpis = dbc.Row([kpi_card('Promedio', prom, 'Promedio en el periodo'), kpi_card('Último registro', ult, f'Cambio: {cambio_pct:.1f}%'), kpi_card('Rango', df_filtrado[metrica].max() - df_filtrado[metrica].min(), 'Max - Min')])

    # Gráficos
    fig_series = px.line(df_filtrado, x='fecha', y=metrica, color='ciudad', template='plotly_dark', markers=False)
    fig_series.update_layout(margin=dict(t=30,l=0,r=0,b=0), legend_title_text='')
    if 'ma7' in opciones:
        for ciudad in df_filtrado['ciudad'].unique():
            sub = df_filtrado[df_filtrado['ciudad'] == ciudad].sort_values('fecha')
            if len(sub) > 7:
                sub['ma7'] = sub[metrica].rolling(7, min_periods=1).mean()
                fig_series.add_traces(go.Scatter(x=sub['fecha'], y=sub['ma7'], mode='lines', name=f'{ciudad} (MA7)', line=dict(width=1, dash='dash')))
    if 'smooth' in opciones:
        fig_series.update_traces(line_shape='spline')

    df_mapa = df_filtrado.groupby('ciudad', as_index=False).agg(lat=('lat','first'), lon=('lon','first'), valor_agregado=(metrica,'mean'))
    fig_map = px.scatter_mapbox(df_mapa, lat='lat', lon='lon', size='valor_agregado', color='valor_agregado', hover_name='ciudad',
                                labels={'valor_agregado': metricas_disponibles[metrica]}, zoom=3.5, center={'lat':-38.4161,'lon':-72.3437}, template='plotly_dark')
    fig_map.update_layout(mapbox_style='carto-darkmatter', margin=dict(t=30,l=0,r=0,b=0))

    df_hist = df[df['ciudad'].isin(df_filtrado['ciudad'].unique())]
    prom_hist_mensual = df_hist.groupby('mes')[metrica].mean()
    prom_filtrado_mensual = df_filtrado.groupby('mes')[metrica].mean()
    df_anom = (prom_filtrado_mensual - prom_hist_mensual).reset_index().rename(columns={metrica: 'anomalia'})
    if not df_anom.empty:
        df_anom['mes'] = df_anom['mes'].astype(int)
        df_anom['color'] = np.where(df_anom['anomalia'] > 0, 'tomato', 'lightblue')
        fig_anom = px.bar(df_anom, x='mes', y='anomalia', template='plotly_dark', labels={'mes':'Mes','anomalia':f'Diferencia ({metricas_disponibles[metrica]})'})
        fig_anom.update_traces(marker_color=df_anom['color'])
        fig_anom.update_layout(xaxis=dict(tickmode='linear'))
    else:
        fig_anom = go.Figure().update_layout(template='plotly_dark', title_text="No hay datos de anomalía para el período.")

    fig_box = px.box(df_filtrado, x='ciudad', y=metrica, points='outliers', template='plotly_dark')
    fig_box.update_layout(showlegend=False)

    return kpis, fig_series, fig_map, fig_anom, fig_box

# --------------------
# 6) EJECUTAR
# --------------------
if __name__ == '__main__':
    app.run(debug=True)