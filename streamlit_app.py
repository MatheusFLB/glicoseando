"""
Streamlit dashboard for Precision Agriculture NDVI Dashboard analysis.

This is the main application that integrates all modules to create
an interactive geospatial analysis dashboard.
"""

import json
from pathlib import Path

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


# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="Precision Agriculture NDVI Analysis Dashboard ",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

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
        st.error(f"Error loading data: {e}")
        return

    # Parse polygon
    try:
        coordinates = parse_polygon_string(request_data["poligono"])
        gdf = create_geodataframe(coordinates)
        polygon_stats = get_polygon_stats(gdf, ndvi_df["ndvi"].mean())
    except (ValueError, KeyError) as e:
        st.error(f"Error processing polygon: {e}")
        return

    # Hidden controls with defaults
    if 'show_peaks' not in st.session_state:
        st.session_state.show_peaks = True

    show_peaks = st.session_state.show_peaks

    # ==================== LAYOUT: CENTER CONTENT ====================
    col_left, col_center, col_right = st.columns([1, 2, 1])

    with col_center:
        # ==================== TITLE & HEADER ====================
        st.markdown("# 🛰️ Precision Agriculture NDVI Analysis Dashboard")
        st.markdown(
            """
            Os dados utilizados neste projeto foram obtidos diretamente do Sistema de Análise Temporal da Vegetação (SATVeg), desenvolvido pela Embrapa, por meio de sua API, usando da integração com o Brazil Data Cube – uma iniciativa do Instituto Nacional de Pesquisas Espaciais (INPE), dedicada à geração, organização e disponibilização de dados a partir de imagens de satélite para o território brasileiro. Essa conexão permite o acesso direto a séries temporais do satélite Sentinel-2, ampliando o potencial de análises ambientais, agropecuárias e de monitoramento territorial.

            O NDVI (Índice de Vegetação por Diferença Normalizada) é uma forma simples e poderosa de medir a “saúde” da vegetação usando imagens de satélite. Ele funciona comparando a quantidade de luz que as plantas refletem: quanto mais verde e vigorosa a vegetação, maior será o valor do NDVI.

            Neste projeto, analiso uma série histórica de mais de 20 anos para entender como a vegetação se comporta ao longo do tempo em uma área agrícola. A proposta não é apenas visualizar dados, mas revelar padrões que ajudam a interpretar o uso da terra e sua dinâmica ao longo dos anos.

            A exploração começa pelo mapa interativo, onde é possível visualizar o NDVI em diferentes datas. Ao alternar entre períodos, o usuário consegue perceber como a vegetação responde ao clima — por exemplo, áreas mais verdes durante a estação chuvosa e redução da vegetação em períodos secos. Esse primeiro contato ajuda a construir uma intuição visual sobre o comportamento da área.
            """
        )

        # ==================== GEOGRAPHIC LOCATION + AREA METRICS ====================
        st.header("🗺️ Geographic Location")

        # Legend below the map
        st.markdown("""
        **📊 NDVI classification legend**

        <span style="background: #8B4513; width: 16px; height: 16px; display: inline-block; border: 1px solid #555; margin-right: 8px;"></span>
        0.0–0.3: Low vegetation  

        <span style="background: #CD853F; width: 16px; height: 16px; display: inline-block; border: 1px solid #555; margin-right: 8px;"></span>
        0.3–0.5: Sparse vegetation  

        <span style="background: #ADFF2F; width: 16px; height: 16px; display: inline-block; border: 1px solid #555; margin-right: 8px;"></span>
        0.5–0.7: Moderate vegetation  

        <span style="background: #32CD32; width: 16px; height: 16px; display: inline-block; border: 1px solid #555; margin-right: 8px;"></span>
        0.7–0.85: High vegetation  

        <span style="background: #006400; width: 16px; height: 16px; display: inline-block; border: 1px solid #555; margin-right: 8px;"></span>
        0.85–1.0: Dense vegetation  

        """, unsafe_allow_html=True)

        # Date picker
        date_range_min = ndvi_df["date"].min().date()
        date_range_max = ndvi_df["date"].max().date()



        selected_date_picker = st.date_input(
            "**Select date to visualize NDVI on map:**",
            value=date_range_max,
            min_value=date_range_min,
            max_value=date_range_max,
            help="Choose a date to view NDVI on the map"
        )

        selected_date = pd.Timestamp(selected_date_picker)
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

        # Process map HTML to make it fully responsive
        map_html = map_html.replace('width: 100%;', 'width: 100%;')
        map_html = map_html.replace('height: 500px;', 'height: 100%;')

        MAP_HEIGHT = 500

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
                height: {MAP_HEIGHT}px;
                min-height: 600px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                overflow: hidden;
            ">
                {map_html}
            </div>
        </div>
        """
        components.v1.html(responsive_html, height=MAP_HEIGHT, scrolling=False)


        # ==================== NDVI TIME SERIES + CHANGE DETECTION (COMBINED) ====================
        st.header("📈 NDVI Time Series Analysis for Land Use Detection")

        st.markdown(
            """
            É nessa visualização que surgem os principais insights, onde o comportamento da vegetação ao longo do tempo fica mais evidente:

            * **Ciclos sazonais**: padrões de subida e descida do NDVI indicam períodos de crescimento e seca;
            * **Picos de vegetação**: associados a momentos de maior vigor, como desenvolvimento de culturas ou recuperação de pastagem;
            * **Quedas abruptas**: podem indicar colheita, seca intensa ou mudança no uso do solo;
            * **Mudanças de padrão ao longo dos anos**: ajudam a identificar transições, como áreas que passaram de pastagem para agricultura.

            Para interpretar corretamente, o ideal é observar:

            * a **frequência dos picos** (uma ou mais safras por ano);
            * a **intensidade dos valores máximos** (nível de produtividade/vigor);
            * e o **comportamento nos períodos secos** (resiliência da vegetação).
            """
        )

        # Year selector for zooming into specific year
        years = sorted(ndvi_df["date"].dt.year.unique())
        selected_year = st.selectbox(
            "Year selection:",
            options=[None] + years,
            format_func=lambda x: "Full Series (2000–2026)" if x is None else str(int(x))
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
                name="Vegetation Peaks",
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
        change_points = []  # Initialize change_points for metrics calculation
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
            xaxis_title="Date",
            yaxis_title="NDVI Value",
            hovermode="x unified",
            template="plotly_white",
            height=chart_height,
            shapes=shapes,
            legend=dict(orientation="v", yanchor="top", y=1.2, xanchor="left", x=0),
        )

        st.plotly_chart(fig, use_container_width=True)

        # Calculate change detection metrics for internal use (not displayed)
        try:
            if change_points:
                deforestation_info = estimate_deforestation_onset(ndvi_df, change_points)
                intensity = calculate_intensity_score(ndvi_df)
        except ImportError:
            pass

        # ==================== ANNUAL METRICS ====================
        st.header("📋 Annual NDVI Trends (2000–2026)")

        st.markdown(
            """
            Por fim, a seção de métricas anuais resume essas informações, permitindo comparar anos diferentes e entender se a área está estável, se houve intensificação do uso agrícola ou possíveis sinais de degradação.

            Esse tipo de análise é extremamente útil para a agricultura, pois permite:

            * monitorar a saúde das lavouras e pastagens;
            * identificar períodos ideais de plantio e colheita;
            * detectar sinais de estresse hídrico;
            * acompanhar a produtividade ao longo do tempo.
            """
        )

        annual_df = extract_annual_metrics(ndvi_df)

        # Annual trend chart
        fig_annual = go.Figure()

        fig_annual.add_trace(go.Scatter(
            x=annual_df["year"],
            y=annual_df["max_ndvi"],
            mode="lines",
            name="Max NDVI",
            line=dict(color="lightgreen", width=1, dash="dash"),
        ))

        fig_annual.add_trace(go.Scatter(
            x=annual_df["year"],
            y=annual_df["mean_ndvi"],
            mode="lines+markers",
            name="Mean NDVI",
            line=dict(color="darkgreen", width=3),
            marker=dict(size=8),
            fill="tozeroy",
            fillcolor="rgba(0,100,0,0.2)",
        ))

        fig_annual.add_trace(go.Scatter(
            x=annual_df["year"],
            y=annual_df["min_ndvi"],
            mode="lines",
            name="Min NDVI",
            line=dict(color="brown", width=1, dash="dash"),
        ))

        fig_annual.update_layout(
            xaxis_title="Year",
            yaxis_title="NDVI Value",
            template="plotly_white",
            height=400,
            legend=dict(orientation="v", yanchor="top", y=1.3, xanchor="left", x=0),
        )

        st.plotly_chart(fig_annual, use_container_width=True)

        # ==================== FOOTER ====================
        st.divider()
        st.markdown(
            """
            <div style="text-align: center; font-size: 14px; line-height: 1.6;">
                <strong>Project Creator:</strong> Matheus Bissoli <br>
                🌐 <a href="https://matheusflb.github.io/" target="_blank">Personal Site</a>
                💼 <a href="https://www.linkedin.com/in/matheusbissoli/" target="_blank">LinkedIn</a> &nbsp;|&nbsp;
                💻 <a href="https://github.com/MatheusFLB" target="_blank">GitHub</a> &nbsp;|&nbsp;
            </div>
            """,
            unsafe_allow_html=True
        )


if __name__ == "__main__":
    main()
