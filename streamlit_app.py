"""
Streamlit dashboard for Precision Agriculture NDVI Dashboard analysis.

This is the main application that integrates all modules to create
an interactive geospatial analysis dashboard with dual-language support.
"""

import json

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from streamlit import components
import folium

from src.data_processing import load_ndvi_data
from src.polygon_processing import (
    parse_polygon_string,
    create_geodataframe,
    get_polygon_stats,
    get_polygon_center,
)
from src.ndvi_analysis import (
    identify_peaks,
    extract_annual_metrics,
)
from src.map_generator import create_full_featured_map, get_color_for_ndvi


# ==================== LANGUAGE DICTIONARY ====================
STRINGS = {
    "pt": {
        "page_title": "Dashboard de Analise NDVI em Agricultura de Precisao",
        "title": "🛰️ Dashboard de Analise NDVI em Agricultura de Precisao",
        "intro": "Os dados utilizados neste projeto foram obtidos diretamente do Sistema de Analise Temporal da Vegetacao (SATVeg), desenvolvido pela Embrapa, por meio de sua API, usando da integracao com o Brazil Data Cube - uma iniciativa do Instituto Nacional de Pesquisas Espaciais (INPE), dedicada a geracao, organizacao e disponibilizacao de dados a partir de imagens de satelite para o territorio brasileiro. Essa conexao permite o acesso direto a series temporais do satelite Sentinel-2, ampliando o potencial de analises ambientais, agropecuarias e de monitoramento territorial.\n\nO NDVI (Indice de Vegetacao por Diferenca Normalizada) e uma forma simples e poderosa de medir a 'saude' da vegetacao usando imagens de satelite. Ele funciona comparando a quantidade de luz que as plantas refletem: quanto mais verde e vigorosa a vegetacao, maior sera o valor do NDVI.\n\nNeste projeto, analiso uma serie historica de mais de 20 anos para entender como a vegetacao se comporta ao longo do tempo em uma area agricola. A proposta nao e apenas visualizar dados, mas revelar padroes que ajudam a interpretar o uso da terra e sua dinamica ao longo dos anos.\n\nA exploracao comeca pelo mapa interativo, onde e possivel visualizar o NDVI em diferentes datas. Ao alternar entre periodos, o usuario consegue perceber como a vegetacao responde ao clima - por exemplo, areas mais verdes durante a estacao chuvosa e reducao da vegetacao em periodos secos. Esse primeiro contato ajuda a construir uma intuicao visual sobre o comportamento da area.",
        "geographic_location": "🗺️ Localizacao Geografica",
        "ndvi_legend": "📊 Legenda de classificacao NDVI",
        "low_vegetation": "Baixa vegetacao",
        "sparse_vegetation": "Vegetacao esparsa",
        "moderate_vegetation": "Vegetacao moderada",
        "high_vegetation": "Alta vegetacao",
        "dense_vegetation": "Vegetacao densa",
        "select_date": "**Selecione a data para visualizar NDVI no mapa:**",
        "select_date_help": "Escolha uma data para visualizar o NDVI no mapa",
        "timeseries_header": "📈 Analise de Serie Temporal NDVI para Deteccao de Mudancas de Uso",
        "timeseries_desc": "E nessa visualizacao que surgem os principais insights, onde o comportamento da vegetacao ao longo do tempo fica mais evidente:\n\n* **Ciclos sazonais**: padroes de subida e descida do NDVI indicam periodos de crescimento e seca;\n* **Picos de vegetacao**: associados a momentos de maior vigor, como desenvolvimento de culturas ou recuperacao de pastagem;\n* **Quedas abruptas**: podem indicar colheita, seca intensa ou mudanca no uso do solo;\n* **Mudancas de padrao ao longo dos anos**: ajudam a identificar transicoes, como areas que passaram de pastagem para agricultura.\n\nPara interpretar corretamente, o ideal e observar:\n\n* a **frequencia dos picos** (uma ou mais safras por ano);\n* a **intensidade dos valores maximos** (nivel de produtividade/vigor);\n* e o **comportamento nos periodos secos** (resiliencia da vegetacao).",
        "year_selection": "Selecao de ano:",
        "full_series": "Serie Completa (2000-2026)",
        "date_label": "Data",
        "ndvi_value": "Valor NDVI",
        "vegetation_peaks": "Picos de Vegetacao",
        "annual_header": "📋 Tendencias NDVI Anuais (2000-2026)",
        "annual_desc": "Por fim, a secao de metricas anuais resume essas informacoes, permitindo comparar anos diferentes e entender se a area esta estavel, se houve intensificacao do uso agricola ou possiveis sinais de degradacao.\n\nEsse tipo de analise e extremamente util para a agricultura, pois permite:\n\n* monitorar a saude das lavouras e pastagens;\n* identificar periodos ideais de plantio e colheita;\n* detectar sinais de estresse hidrico;\n* acompanhar a produtividade ao longo do tempo.",
        "max_ndvi": "NDVI Maximo",
        "mean_ndvi": "NDVI Medio",
        "min_ndvi": "NDVI Minimo",
        "year": "Ano",
        "error_loading": "Erro ao carregar dados:",
        "error_polygon": "Erro ao processar poligono:",
        "creator": "Criador do Projeto:",
        "personal_site": "Site Pessoal",
    },
    "en": {
        "page_title": "Precision Agriculture NDVI Analysis Dashboard",
        "title": "🛰️ Precision Agriculture NDVI Analysis Dashboard",
        "intro": "The data used in this project was obtained directly from the Temporal Vegetation Analysis System (SATVeg), developed by Embrapa, through its API, leveraging integration with the Brazil Data Cube - an initiative by the National Institute for Space Research (INPE), dedicated to the generation, organization, and provision of satellite imagery data for Brazilian territory. This connection enables direct access to Sentinel-2 satellite time series, expanding the potential for environmental, agricultural, and territorial monitoring analyses.\n\nNDVI (Normalized Difference Vegetation Index) is a simple yet powerful way to measure vegetation 'health' using satellite imagery. It works by comparing the amount of light reflected by plants: the greener and more vigorous the vegetation, the higher the NDVI value.\n\nIn this project, I analyze over 20 years of historical data to understand how vegetation behaves over time in an agricultural area. The goal is not just to visualize data, but to reveal patterns that help interpret land use and its dynamics throughout the years.\n\nThe exploration begins with an interactive map, where you can visualize NDVI at different dates. By switching between periods, users can perceive how vegetation responds to climate - for example, greener areas during the rainy season and reduced vegetation in dry periods. This initial contact helps build visual intuition about the area's behavior.",
        "geographic_location": "🗺️ Geographic Location",
        "ndvi_legend": "📊 NDVI Classification Legend",
        "low_vegetation": "Low vegetation",
        "sparse_vegetation": "Sparse vegetation",
        "moderate_vegetation": "Moderate vegetation",
        "high_vegetation": "High vegetation",
        "dense_vegetation": "Dense vegetation",
        "select_date": "**Select date to visualize NDVI on map:**",
        "select_date_help": "Choose a date to view NDVI on the map",
        "timeseries_header": "📈 NDVI Time Series Analysis for Land Use Change Detection",
        "timeseries_desc": "This visualization reveals the main insights, where vegetation behavior over time becomes more evident:\n\n* **Seasonal cycles**: patterns of rise and fall in NDVI indicate growth and dry periods;\n* **Vegetation peaks**: associated with moments of greater vigor, such as crop development or pasture recovery;\n* **Abrupt declines**: may indicate harvesting, intense drought, or land-use change;\n* **Pattern changes over years**: help identify transitions, such as areas that shifted from pasture to agriculture.\n\nTo interpret correctly, it's ideal to observe:\n\n* the **frequency of peaks** (one or more harvests per year);\n* the **intensity of maximum values** (productivity/vigor level);\n* and the **behavior during dry periods** (vegetation resilience).",
        "year_selection": "Year selection:",
        "full_series": "Full Series (2000-2026)",
        "date_label": "Date",
        "ndvi_value": "NDVI Value",
        "vegetation_peaks": "Vegetation Peaks",
        "annual_header": "📋 Annual NDVI Trends (2000-2026)",
        "annual_desc": "Finally, the annual metrics section summarizes this information, allowing comparison between different years and understanding whether the area is stable, if there has been intensification of agricultural use, or possible signs of degradation.\n\nThis type of analysis is extremely useful for agriculture, as it allows:\n\n* monitoring crop and pasture health;\n* identifying ideal planting and harvesting periods;\n* detecting signs of water stress;\n* tracking productivity over time.",
        "max_ndvi": "Max NDVI",
        "mean_ndvi": "Mean NDVI",
        "min_ndvi": "Min NDVI",
        "year": "Year",
        "error_loading": "Error loading data:",
        "error_polygon": "Error processing polygon:",
        "creator": "Project Creator:",
        "personal_site": "Personal Site",
    }
}


# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="Precision Agriculture NDVI Analysis Dashboard",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==================== LANGUAGE SELECTOR ====================
if 'language' not in st.session_state:
    st.session_state.language = 'en'

col_lang_left, col_lang_center, col_lang_right = st.columns([3, 1, 1])
with col_lang_right:
    selected_lang = st.selectbox(
        "Language / Idioma:",
        options=["en", "pt"],
        format_func=lambda x: "🌎 English" if x == "en" else "🇧🇷 Portugues",
        key="lang_selector"
    )
    st.session_state.language = selected_lang

lang = st.session_state.language
txt = STRINGS[lang]

# ==================== CUSTOM STYLING ====================
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    </style>
""", unsafe_allow_html=True)

# ==================== DATA LOADING ====================
@st.cache_resource
def load_all_data():
    """Load all data files."""
    ndvi_df = load_ndvi_data("data/ndvi_timeseries.json")

    with open("data/ndvi_request.json", "r", encoding="utf-8") as f:
        request_data = json.load(f)

    return ndvi_df, request_data


# ==================== MAIN APP ====================
def main():
    # Load data
    try:
        ndvi_df, request_data = load_all_data()
    except FileNotFoundError as e:
        st.error(f"{txt['error_loading']} {e}")
        return

    # Parse polygon
    try:
        coordinates = parse_polygon_string(request_data["poligono"])
        gdf = create_geodataframe(coordinates)
        polygon_stats = get_polygon_stats(gdf, ndvi_df["ndvi"].mean())
    except (ValueError, KeyError) as e:
        st.error(f"{txt['error_polygon']} {e}")
        return

    # Hidden controls with defaults
    if 'show_peaks' not in st.session_state:
        st.session_state.show_peaks = True

    show_peaks = st.session_state.show_peaks

    # ==================== LAYOUT: CENTER CONTENT ====================
    col_left, col_center, col_right = st.columns([1, 2, 1])

    with col_center:
        # ==================== TITLE & HEADER ====================
        st.markdown(f"# {txt['title']}")
        st.markdown(txt['intro'])

        # ==================== GEOGRAPHIC LOCATION + AREA METRICS ====================
        st.header(txt['geographic_location'])

        # Legend below the map
        legend_html = f"""
        **{txt['ndvi_legend']}**

        <span style="background: #8B4513; width: 16px; height: 16px; display: inline-block; border: 1px solid #555; margin-right: 8px;"></span>
        0.0-0.3: {txt['low_vegetation']}

        <span style="background: #CD853F; width: 16px; height: 16px; display: inline-block; border: 1px solid #555; margin-right: 8px;"></span>
        0.3-0.5: {txt['sparse_vegetation']}

        <span style="background: #ADFF2F; width: 16px; height: 16px; display: inline-block; border: 1px solid #555; margin-right: 8px;"></span>
        0.5-0.7: {txt['moderate_vegetation']}

        <span style="background: #32CD32; width: 16px; height: 16px; display: inline-block; border: 1px solid #555; margin-right: 8px;"></span>
        0.7-0.85: {txt['high_vegetation']}

        <span style="background: #006400; width: 16px; height: 16px; display: inline-block; border: 1px solid #555; margin-right: 8px;"></span>
        0.85-1.0: {txt['dense_vegetation']}

        """
        st.markdown(legend_html, unsafe_allow_html=True)

        # Date picker
        date_range_min = ndvi_df["date"].min().date()
        date_range_max = ndvi_df["date"].max().date()

        selected_date_picker = st.date_input(
            txt['select_date'],
            value=date_range_max,
            min_value=date_range_min,
            max_value=date_range_max,
            help=txt['select_date_help']
        )

        idx = (ndvi_df['date'].dt.date - selected_date_picker).abs().argmin()
        closest_date = ndvi_df.iloc[idx]["date"]
        ndvi_at_date = ndvi_df.iloc[idx]["ndvi"]

        # Create and display interactive map
        center = get_polygon_center(gdf)
        m = create_full_featured_map(
            gdf,
            center,
            ndvi_at_date,
            polygon_stats["area_ha"],
        )

        map_html = m._repr_html_()

        # Perfectly centered vertical responsive map container
        responsive_html = f"""
        <div style="
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
            margin: 20px auto;
        ">
            <div style="
                width: 100%;
                max-width: 800px;
                height: 800px;
                min-height: 600px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                overflow: hidden;
            ">
                {map_html}
            </div>
        </div>
        """
        components.v1.html(responsive_html, height=800, scrolling=False)

        # ==================== NDVI TIME SERIES + CHANGE DETECTION (COMBINED) ====================
        st.header(txt['timeseries_header'])

        st.markdown(txt['timeseries_desc'])

        # Year selector for zooming into specific year
        years = sorted(ndvi_df["date"].dt.year.unique())
        selected_year = st.selectbox(
            txt['year_selection'],
            options=[None] + years,
            format_func=lambda x: txt['full_series'] if x is None else str(int(x))
        )

        # Prepare data
        ndvi_df_plot = ndvi_df.copy()

        # Filter by year if selected
        if selected_year:
            year_mask = ndvi_df_plot["date"].dt.year == selected_year
            ndvi_df_plot = ndvi_df_plot[year_mask]

        peaks_idx = identify_peaks(ndvi_df_plot["ndvi"], prominence=0.08)

        # Create main figure
        fig = go.Figure()

        # Peaks
        if show_peaks and len(peaks_idx) > 0:
            fig.add_trace(go.Scatter(
                x=ndvi_df_plot.iloc[peaks_idx]["date"],
                y=ndvi_df_plot.iloc[peaks_idx]["ndvi"],
                mode="markers",
                name=txt['vegetation_peaks'],
                marker=dict(size=8, color="red", symbol="star"),
            ))

        # Raw NDVI only
        fig.add_trace(go.Scatter(
            x=ndvi_df_plot["date"],
            y=ndvi_df_plot["ndvi"],
            mode="lines",
            name="NDVI",
            line=dict(color="steelblue", width=2),
        ))

        # Add year boundary markers (only for full series)
        shapes = []
        if not selected_year:
            # Show red dashed lines at year boundaries for full temporal range
            years_in_range = sorted(ndvi_df["date"].dt.year.unique())
            for year in years_in_range[1:]:  # Skip first year, show from 2nd year onwards
                year_start = pd.Timestamp(year=year, month=1, day=1)
                if year_start >= ndvi_df["date"].min() and year_start <= ndvi_df["date"].max():
                    shapes.append(dict(
                        type="line",
                        x0=year_start,
                        x1=year_start,
                        y0=0,
                        y1=1,
                        yref="paper",
                        line=dict(color="red", width=1.5, dash="dash"),
                    ))

        # Dynamic height based on year selection (taller for zoomed view)
        chart_height = 700 if selected_year else 500

        fig.update_layout(
            xaxis_title=txt['date_label'],
            yaxis_title=txt['ndvi_value'],
            hovermode="x unified",
            template="plotly_white",
            height=chart_height,
            shapes=shapes,
            legend=dict(orientation="v", yanchor="top", y=1.2, xanchor="left", x=0),
        )

        st.plotly_chart(fig, use_container_width=True)

        # ==================== ANNUAL METRICS ====================
        st.header(txt['annual_header'])

        st.markdown(txt['annual_desc'])

        annual_df = extract_annual_metrics(ndvi_df)

        # Annual trend chart
        fig_annual = go.Figure()

        fig_annual.add_trace(go.Scatter(
            x=annual_df["year"],
            y=annual_df["max_ndvi"],
            mode="lines",
            name=txt['max_ndvi'],
            line=dict(color="lightgreen", width=1, dash="dash"),
        ))

        fig_annual.add_trace(go.Scatter(
            x=annual_df["year"],
            y=annual_df["mean_ndvi"],
            mode="lines+markers",
            name=txt['mean_ndvi'],
            line=dict(color="darkgreen", width=3),
            marker=dict(size=8),
            fill="tozeroy",
            fillcolor="rgba(0,100,0,0.2)",
        ))

        fig_annual.add_trace(go.Scatter(
            x=annual_df["year"],
            y=annual_df["min_ndvi"],
            mode="lines",
            name=txt['min_ndvi'],
            line=dict(color="brown", width=1, dash="dash"),
        ))

        fig_annual.update_layout(
            xaxis_title=txt['year'],
            yaxis_title=txt['ndvi_value'],
            template="plotly_white",
            height=400,
            legend=dict(orientation="v", yanchor="top", y=1.3, xanchor="left", x=0),
        )

        st.plotly_chart(fig_annual, use_container_width=True)

        # ==================== FOOTER ====================
        st.divider()
        st.markdown(
            f"""
            <div style="text-align: center; font-size: 14px; line-height: 1.6;">
                <strong>{txt['creator']}</strong> Matheus Bissoli <br>
                🌐 <a href="https://matheusflb.github.io/" target="_blank">{txt['personal_site']}</a>
                💼 <a href="https://www.linkedin.com/in/matheusbissoli/" target="_blank">LinkedIn</a> &nbsp;|&nbsp;
                💻 <a href="https://github.com/MatheusFLB" target="_blank">GitHub</a>
            </div>
            """,
            unsafe_allow_html=True
        )


if __name__ == "__main__":
    main()
