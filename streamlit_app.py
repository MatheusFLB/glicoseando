"""
DASHBOARD STREAMLIT PARA ANÁLISE NDVI EM AGRICULTURA DE PRECISÃO

Este é o arquivo principal da aplicação que integra todos os módulos para criar
um dashboard interativo de análise geoespacial com suporte a dois idiomas (português e inglês).

O dashboard analisa séries temporais do NDVI (Índice de Vegetação por Diferença Normalizada)
obtidas do SATVeg/Embrapa para monitorar a saúde da vegetação em áreas agrícolas ao longo
de mais de 20 anos (2000-2026).

FUNCIONALIDADES PRINCIPAIS:
- Mapa interativo com visualização do NDVI em diferentes datas
- Análise de série temporal com detecção de picos de vegetação
- Análise de tendências anuais do NDVI
- Suporte a dois idiomas (PT/EN)
- Cálculo de estatísticas por polígono (área, NDVI médio, etc)
"""

import json

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from streamlit import components
import folium

# Importação dos módulos de processamento de dados
from src.data_processing import load_ndvi_data
from src.polygon_processing import (
    parse_polygon_string,
    create_geodataframe,
    get_polygon_stats,
    get_polygon_center,
)
from src.ndvi_analysis import (
    identify_peaks,  # Função para detectar picos de vegetação
    extract_annual_metrics,  # Função para extrair estatísticas anuais
)
from src.map_generator import create_full_featured_map, get_color_for_ndvi


# ==================== DICIONÁRIO DE IDIOMAS ====================
# Dicionário centralizado que contém todas as strings da aplicação em português e inglês.
# Permite fácil alternância entre idiomas sem necessidade de tradução ao longo do código.
STRINGS = {
    # PORTUGUÊS
    "pt": {
        # Títulos e cabeçalhos principais
        "page_title": "Dashboard de Análise NDVI em Agricultura de Precisão",
        "title": "🛰️ Dashboard de Análise NDVI em Agricultura de Precisão",

        # Introdução explicando o projeto e os dados utilizados
        "intro": "Os dados utilizados neste projeto foram obtidos diretamente do Sistema de Análise Temporal da Vegetação (SATVeg), desenvolvido pela Embrapa, por meio de sua API, usando da integração com o Brazil Data Cube - uma iniciativa do Instituto Nacional de Pesquisas Espaciais (INPE), dedicada à geração, organização e disponibilização de dados a partir de imagens de satélite para o território brasileiro. Essa conexão permite o acesso direto a séries temporais do satélite Sentinel-2, ampliando o potencial de análises ambientais, agropecuárias e de monitoramento territorial.\n\nO NDVI (Índice de Vegetação por Diferença Normalizada) é uma forma simples e poderosa de medir a 'saúde' da vegetação usando imagens de satélite. Ele funciona comparando a quantidade de luz que as plantas refletem: quanto mais verde e vigorosa a vegetação, maior será o valor do NDVI.\n\nNeste projeto, analiso uma série histórica de mais de 20 anos para entender como a vegetação se comporta ao longo do tempo em uma área agrícola. A proposta não é apenas visualizar dados, mas revelar padrões que ajudam a interpretar o uso da terra e sua dinâmica ao longo dos anos.\n\nA exploração começa pelo mapa interativo, onde é possível visualizar o NDVI em diferentes datas. Ao alternar entre períodos, o usuário consegue perceber como a vegetação responde ao clima - por exemplo, áreas mais verdes durante a estação chuvosa e redução da vegetação em períodos secos. Esse primeiro contato ajuda a construir uma intuição visual sobre o comportamento da área.",

        # Seção de localização geográfica
        "geographic_location": "🗺️ Localização Geográfica",
        "ndvi_legend": "📊 Legenda de classificação NDVI",
        "low_vegetation": "Baixa vegetação",
        "sparse_vegetation": "Vegetação esparsa",
        "moderate_vegetation": "Vegetação moderada",
        "high_vegetation": "Alta vegetação",
        "dense_vegetation": "Vegetação densa",

        # Seletor de data
        "select_date": "**Selecione a data para visualizar NDVI no mapa:**",
        "select_date_help": "Escolha uma data para visualizar o NDVI no mapa",

        # Seção de série temporal
        "timeseries_header": "📈 Análise de Série Temporal NDVI para Detecção de Mudanças de Uso",
        "timeseries_desc": "É nessa visualização que surgem os principais insights, onde o comportamento da vegetação ao longo do tempo fica mais evidente:\n\n* **Ciclos sazonais**: padrões de subida e descida do NDVI indicam períodos de crescimento e seca;\n* **Picos de vegetação**: associados a momentos de maior vigor, como desenvolvimento de culturas ou recuperação de pastagem;\n* **Quedas abruptas**: podem indicar colheita, seca intensa ou mudança no uso do solo;\n* **Mudanças de padrão ao longo dos anos**: ajudam a identificar transições, como áreas que passaram de pastagem para agricultura.\n\nPara interpretar corretamente, o ideal é observar:\n\n* a **frequência dos picos** (uma ou mais safras por ano);\n* a **intensidade dos valores máximos** (nível de produtividade/vigor);\n* e o **comportamento nos períodos secos** (resiliência da vegetação).",
        "year_selection": "Seleção de ano:",
        "full_series": "Série Completa (2000-2026)",
        "date_label": "Data",
        "ndvi_value": "Valor NDVI",
        "vegetation_peaks": "Picos de Vegetação",

        # Seção de métricas anuais
        "annual_header": "📋 Tendências NDVI Anuais (2000-2026)",
        "annual_desc": "Por fim, a seção de métricas anuais resume essas informações, permitindo comparar anos diferentes e entender se a área está estável, se houve intensificação do uso agrícola ou possíveis sinais de degradação.\n\nEsse tipo de análise é extremamente útil para a agricultura, pois permite:\n\n* monitorar a saúde das lavouras e pastagens;\n* identificar períodos ideais de plantio e colheita;\n* detectar sinais de estresse hídrico;\n* acompanhar a produtividade ao longo do tempo.",
        "max_ndvi": "NDVI Máximo",
        "mean_ndvi": "NDVI Médio",
        "min_ndvi": "NDVI Mínimo",
        "year": "Ano",

        # Mensagens de erro
        "error_loading": "Erro ao carregar dados:",
        "error_polygon": "Erro ao processar polígono:",

        # Informações do criador
        "creator": "Criador do Projeto:",
        "personal_site": "Site Pessoal",
    },

    # ENGLISH
    "en": {
        # Main titles and headers
        "page_title": "Precision Agriculture NDVI Analysis Dashboard",
        "title": "🛰️ Precision Agriculture NDVI Analysis Dashboard",

        # Introduction explaining the project and data sources
        "intro": "The data used in this project was obtained directly from the Temporal Vegetation Analysis System (SATVeg), developed by Embrapa, through its API, leveraging integration with the Brazil Data Cube - an initiative by the National Institute for Space Research (INPE), dedicated to the generation, organization, and provision of satellite imagery data for Brazilian territory. This connection enables direct access to Sentinel-2 satellite time series, expanding the potential for environmental, agricultural, and territorial monitoring analyses.\n\nNDVI (Normalized Difference Vegetation Index) is a simple yet powerful way to measure vegetation 'health' using satellite imagery. It works by comparing the amount of light reflected by plants: the greener and more vigorous the vegetation, the higher the NDVI value.\n\nIn this project, I analyze over 20 years of historical data to understand how vegetation behaves over time in an agricultural area. The goal is not just to visualize data, but to reveal patterns that help interpret land use and its dynamics throughout the years.\n\nThe exploration begins with an interactive map, where you can visualize NDVI at different dates. By switching between periods, users can perceive how vegetation responds to climate - for example, greener areas during the rainy season and reduced vegetation in dry periods. This initial contact helps build visual intuition about the area's behavior.",

        # Geographic location section
        "geographic_location": "🗺️ Geographic Location",
        "ndvi_legend": "📊 NDVI Classification Legend",
        "low_vegetation": "Low vegetation",
        "sparse_vegetation": "Sparse vegetation",
        "moderate_vegetation": "Moderate vegetation",
        "high_vegetation": "High vegetation",
        "dense_vegetation": "Dense vegetation",

        # Date selector
        "select_date": "**Select date to visualize NDVI on map:**",
        "select_date_help": "Choose a date to view NDVI on the map",

        # Time series section
        "timeseries_header": "📈 NDVI Time Series Analysis for Land Use Change Detection",
        "timeseries_desc": "This visualization reveals the main insights, where vegetation behavior over time becomes more evident:\n\n* **Seasonal cycles**: patterns of rise and fall in NDVI indicate growth and dry periods;\n* **Vegetation peaks**: associated with moments of greater vigor, such as crop development or pasture recovery;\n* **Abrupt declines**: may indicate harvesting, intense drought, or land-use change;\n* **Pattern changes over years**: help identify transitions, such as areas that shifted from pasture to agriculture.\n\nTo interpret correctly, it's ideal to observe:\n\n* the **frequency of peaks** (one or more harvests per year);\n* the **intensity of maximum values** (productivity/vigor level);\n* and the **behavior during dry periods** (vegetation resilience).",
        "year_selection": "Year selection:",
        "full_series": "Full Series (2000-2026)",
        "date_label": "Date",
        "ndvi_value": "NDVI Value",
        "vegetation_peaks": "Vegetation Peaks",

        # Annual metrics section
        "annual_header": "📋 Annual NDVI Trends (2000-2026)",
        "annual_desc": "Finally, the annual metrics section summarizes this information, allowing comparison between different years and understanding whether the area is stable, if there has been intensification of agricultural use, or possible signs of degradation.\n\nThis type of analysis is extremely useful for agriculture, as it allows:\n\n* monitoring crop and pasture health;\n* identifying ideal planting and harvesting periods;\n* detecting signs of water stress;\n* tracking productivity over time.",
        "max_ndvi": "Max NDVI",
        "mean_ndvi": "Mean NDVI",
        "min_ndvi": "Min NDVI",
        "year": "Year",

        # Error messages
        "error_loading": "Error loading data:",
        "error_polygon": "Error processing polygon:",

        # Creator information
        "creator": "Project Creator:",
        "personal_site": "Personal Site",
    }
}


# ==================== CONFIGURAÇÃO DA PÁGINA ====================
# Define as configurações visuais e de layout do Streamlit
st.set_page_config(
    page_title="Precision Agriculture NDVI Analysis Dashboard",
    page_icon="🛰️",  # Ícone dos satélites
    layout="wide",  # Layout amplo para melhor aproveitamento do espaço
    initial_sidebar_state="collapsed",  # Sidebar inicialmente recolhida
)

# ==================== SELETOR DE IDIOMA ====================
# Sistema de sessão do Streamlit para manter o idioma selecionado durante a navegação
if 'language' not in st.session_state:
    # Define inglês como idioma padrão se ainda não foi selecionado
    st.session_state.language = 'en'

# Cria três colunas: esquerda (vazia), centro (vazia), direita (seletor de idioma)
col_lang_left, col_lang_center, col_lang_right = st.columns([3, 1, 1])
with col_lang_right:
    # Seletor de idioma que permite escolher entre Inglês e Português
    selected_lang = st.selectbox(
        "Language / Idioma:",
        options=["en", "pt"],
        format_func=lambda x: "🌎 English" if x == "en" else "🇧🇷 Portugues",
        key="lang_selector"
    )
    st.session_state.language = selected_lang

# Obtém o idioma selecionado e carrega as strings correspondentes
lang = st.session_state.language
txt = STRINGS[lang]

# ==================== ESTILO PERSONALIZADO ====================
# CSS customizado para melhorar a aparência visual do dashboard
# Aplica um gradiente de cor de fundo
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    </style>
""", unsafe_allow_html=True)

# ==================== CARREGAMENTO DE DADOS ====================
# Decorador @st.cache_resource cacheiza os dados - carrega uma vez e reutiliza
# Melhora significativamente o desempenho ao evitar recarregamentos desnecessários
@st.cache_resource
def load_all_data():
    """
    Carrega todos os arquivos de dados necessários para o dashboard.

    Returns:
        tuple: (ndvi_df, request_data)
            - ndvi_df: DataFrame com série temporal de NDVI
            - request_data: Dicionário com dados da requisição (polígono, etc)
    """
    # Carrega os dados de série temporal do NDVI do arquivo JSON
    ndvi_df = load_ndvi_data("data/ndvi_timeseries.json")

    # Carrega os dados de requisição (que contém o polígono de interesse)
    with open("data/ndvi_request.json", "r", encoding="utf-8") as f:
        request_data = json.load(f)

    return ndvi_df, request_data


# ==================== APLICAÇÃO PRINCIPAL ====================
def main():
    """
    Função principal que orquestra todo o fluxo da aplicação.

    FLUXO:
    1. Carrega dados de NDVI e requisição
    2. Processa as coordenadas do polígono
    3. Exibe mapa interativo com seletor de data
    4. Mostra gráfico de série temporal com picos de vegetação
    5. Exibe tendências anuais em gráfico separado
    6. Rodapé com informações do criador
    """
    # ==================== CARREGAMENTO E VALIDAÇÃO DE DADOS ====================
    # Tenta carregar os dados, exibindo erro se houver problema
    try:
        ndvi_df, request_data = load_all_data()
    except FileNotFoundError as e:
        # Se os arquivos de dados não existem, exibe mensagem de erro
        st.error(f"{txt['error_loading']} {e}")
        return  # Interrompe a execução da aplicação

    # ==================== PROCESSAMENTO DO POLÍGONO ====================
    # Processa as coordenadas do polígono fornecidas na requisição
    try:
        # Extrai as coordenadas do polígono do formato string
        coordinates = parse_polygon_string(request_data["poligono"])

        # Cria um GeoDataFrame a partir das coordenadas (estrutura geoespacial)
        gdf = create_geodataframe(coordinates)

        # Calcula estatísticas do polígono (área, centro, NDVI médio, etc)
        polygon_stats = get_polygon_stats(gdf, ndvi_df["ndvi"].mean())
    except (ValueError, KeyError) as e:
        # Se há erro no processamento do polígono, exibe mensagem de erro
        st.error(f"{txt['error_polygon']} {e}")
        return  # Interrompe a execução

    # ==================== CONTROLES OCULTOS ====================
    # Inicializa o estado de exibição de picos se não existir
    # (picos são marcadores dos valores máximos de NDVI)
    if 'show_peaks' not in st.session_state:
        st.session_state.show_peaks = True

    show_peaks = st.session_state.show_peaks

    # ==================== LAYOUT: CENTRALIZAR CONTEÚDO ====================
    # Cria três colunas para centralizar o conteúdo (esquerda vazia, centro conteúdo, direita vazia)
    col_left, col_center, col_right = st.columns([1, 2, 1])

    with col_center:
        # ==================== TÍTULO E INTRODUÇÃO ====================
        st.markdown(f"# {txt['title']}")  # Título principal
        st.markdown(txt['intro'])  # Texto introdutório explicativo

        # ==================== LOCALIZAÇÃO GEOGRÁFICA + MAPA ====================
        st.header(txt['geographic_location'])  # Cabeçalho da seção

        # Cria e exibe a legenda de classificação NDVI
        # A legenda mostra os intervalos de cores para diferentes níveis de vegetação
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

        # ==================== SELETOR DE DATA ====================
        # Permite ao usuário escolher uma data para visualizar o NDVI no mapa
        date_range_min = ndvi_df["date"].min().date()
        date_range_max = ndvi_df["date"].max().date()

        selected_date_picker = st.date_input(
            txt['select_date'],
            value=date_range_max,  # Data inicial: a mais recente
            min_value=date_range_min,  # Data mínima disponível
            max_value=date_range_max,  # Data máxima disponível
            help=txt['select_date_help']
        )

        # Encontra a data mais próxima na série temporal à data selecionada
        # (já que nem todas as datas estão disponíveis no arquivo de dados)
        idx = (ndvi_df['date'].dt.date - selected_date_picker).abs().argmin()
        closest_date = ndvi_df.iloc[idx]["date"]
        ndvi_at_date = ndvi_df.iloc[idx]["ndvi"]

        # ==================== CRIAÇÃO E EXIBIÇÃO DO MAPA ====================
        # Obtém as coordenadas do centro do polígono para centralizar o mapa
        center = get_polygon_center(gdf)

        # Cria um mapa interativo com o polígono colorido de acordo com o NDVI
        m = create_full_featured_map(
            gdf,  # Dados geométricos do polígono
            center,  # Coordenadas para centrar o mapa
            ndvi_at_date,  # Valor de NDVI para colorir o polígono
            polygon_stats["area_ha"],  # Área do polígono em hectares
        )

        # Obtém o HTML do mapa para exibição
        map_html = m._repr_html_()

        # Cria um container HTML responsivo para o mapa com estilo personalizado
        # Garante que o mapa seja exibido de forma centralizada e bem formatado
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
                height: 400px;
                min-height: 400px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                overflow: hidden;
            ">
                {map_html}
            </div>
        </div>
        """
        # Exibe o mapa no Streamlit com altura de 400px
        components.v1.html(responsive_html, height=400, scrolling=False)

        # ==================== ANÁLISE DE SÉRIE TEMPORAL + DETECÇÃO DE MUDANÇAS ====================
        st.header(txt['timeseries_header'])  # Cabeçalho da seção

        st.markdown(txt['timeseries_desc'])  # Descrição explicativa

        # Seletor de ano para permitir zoom em um período específico
        # Útil para examinar padrões em anos individuais
        years = sorted(ndvi_df["date"].dt.year.unique())
        selected_year = st.selectbox(
            txt['year_selection'],
            options=[None] + years,  # None = série completa
            format_func=lambda x: txt['full_series'] if x is None else str(int(x))
        )

        # Prepara uma cópia dos dados para plotagem
        ndvi_df_plot = ndvi_df.copy()

        # Se um ano foi selecionado, filtra apenas os dados daquele ano
        if selected_year:
            year_mask = ndvi_df_plot["date"].dt.year == selected_year
            ndvi_df_plot = ndvi_df_plot[year_mask]

        # Detecta os picos (máximos locais) na série de NDVI
        # Picos representam momentos de maior vigor vegetativo (crescimento máximo)
        peaks_idx = identify_peaks(ndvi_df_plot["ndvi"], prominence=0.08)

        # ==================== CRIAÇÃO DO GRÁFICO DE SÉRIE TEMPORAL ====================
        fig = go.Figure()

        # Adiciona os picos como marcadores vermelhos (estrelas) no gráfico
        # Ajuda a identificar visualmente os períodos de pico de vegetação
        if show_peaks and len(peaks_idx) > 0:
            fig.add_trace(go.Scatter(
                x=ndvi_df_plot.iloc[peaks_idx]["date"],
                y=ndvi_df_plot.iloc[peaks_idx]["ndvi"],
                mode="markers",
                name=txt['vegetation_peaks'],
                marker=dict(size=8, color="red", symbol="star"),
            ))

        # Adiciona a série de NDVI como linha azul
        # Mostra a evolução temporal contínua dos valores de NDVI
        fig.add_trace(go.Scatter(
            x=ndvi_df_plot["date"],
            y=ndvi_df_plot["ndvi"],
            mode="lines",
            name="NDVI",
            line=dict(color="steelblue", width=2),
        ))

        # ==================== MARCADORES DE LIMITES DE ANOS ====================
        # Adiciona linhas vermelhas tracejadas nos limites entre anos
        # Facilita a visualização de limites anuais na série temporal
        shapes = []
        if not selected_year:
            # Mostra as linhas apenas quando toda a série está sendo visualizada
            years_in_range = sorted(ndvi_df["date"].dt.year.unique())
            for year in years_in_range[1:]:  # Começa do segundo ano
                year_start = pd.Timestamp(year=year, month=1, day=1)
                # Verifica se a data está dentro do intervalo de dados
                if year_start >= ndvi_df["date"].min() and year_start <= ndvi_df["date"].max():
                    shapes.append(dict(
                        type="line",
                        x0=year_start,
                        x1=year_start,
                        y0=0,
                        y1=1,
                        yref="paper",  # Posição relativa ao eixo Y
                        line=dict(color="red", width=1.5, dash="dash"),
                    ))

        # Altura do gráfico varia conforme a visualização
        # Gráfico de um ano é mais alto para permitir melhor inspeção
        chart_height = 700 if selected_year else 500

        # Configura o layout do gráfico
        fig.update_layout(
            xaxis_title=txt['date_label'],  # Rótulo do eixo X
            yaxis_title=txt['ndvi_value'],  # Rótulo do eixo Y
            hovermode="x unified",  # Mostra informações de todos os traços ao passar o mouse
            template="plotly_white",  # Tema visual (fundo branco)
            height=chart_height,
            shapes=shapes,  # Adiciona as linhas de limite de anos
            legend=dict(orientation="v", yanchor="top", y=1.2, xanchor="left", x=0),
        )

        # Exibe o gráfico Plotly
        st.plotly_chart(fig, use_container_width=True)

        # ==================== MÉTRICAS E TENDÊNCIAS ANUAIS ====================
        st.header(txt['annual_header'])  # Cabeçalho da seção

        st.markdown(txt['annual_desc'])  # Descrição explicativa

        # Extrai as estatísticas anuais (média, máximo, mínimo de NDVI por ano)
        annual_df = extract_annual_metrics(ndvi_df)

        # ==================== GRÁFICO DE TENDÊNCIAS ANUAIS ====================
        fig_annual = go.Figure()

        # Adiciona linha tracejada com valores máximos anuais de NDVI
        # Mostra o melhor desempenho da vegetação em cada ano
        fig_annual.add_trace(go.Scatter(
            x=annual_df["year"],
            y=annual_df["max_ndvi"],
            mode="lines",
            name=txt['max_ndvi'],
            line=dict(color="lightgreen", width=1, dash="dash"),
        ))

        # Adiciona linha contínua com valores médios anuais de NDVI
        # Esta é a principal métrica - mostra o desempenho médio
        # A área preenchida sob a linha facilita a visualização da tendência
        fig_annual.add_trace(go.Scatter(
            x=annual_df["year"],
            y=annual_df["mean_ndvi"],
            mode="lines+markers",  # Mostrar linha e marcadores
            name=txt['mean_ndvi'],
            line=dict(color="darkgreen", width=3),
            marker=dict(size=8),
            fill="tozeroy",  # Preencher a área sob a curva
            fillcolor="rgba(0,100,0,0.2)",  # Cor de preenchimento semi-transparente
        ))

        # Adiciona linha tracejada com valores mínimos anuais de NDVI
        # Mostra o pior desempenho da vegetação em cada ano
        fig_annual.add_trace(go.Scatter(
            x=annual_df["year"],
            y=annual_df["min_ndvi"],
            mode="lines",
            name=txt['min_ndvi'],
            line=dict(color="brown", width=1, dash="dash"),
        ))

        # Configura o layout do gráfico anual
        fig_annual.update_layout(
            xaxis_title=txt['year'],  # Rótulo do eixo X (anos)
            yaxis_title=txt['ndvi_value'],  # Rótulo do eixo Y (valores NDVI)
            template="plotly_white",  # Tema visual
            height=400,  # Altura do gráfico
            legend=dict(orientation="v", yanchor="top", y=1.3, xanchor="left", x=0),
        )

        # Exibe o gráfico de tendências anuais
        st.plotly_chart(fig_annual, use_container_width=True)

        # ==================== RODAPÉ COM INFORMAÇÕES DO CRIADOR ====================
        st.divider()  # Linha divisória
        st.markdown(
            f"""
            <div style="text-align: center; font-size: 14px; line-height: 1.6;">
                <strong>{txt['creator']}</strong> Matheus Bissoli <br>
                🌐 <a href="https://matheusflb.github.io/" target="_blank">{txt['personal_site']}</a> &nbsp;|&nbsp;
                💼 <a href="https://www.linkedin.com/in/matheusbissoli/" target="_blank">LinkedIn</a> &nbsp;|&nbsp;
                💻 <a href="https://github.com/MatheusFLB/" target="_blank">GitHub</a> &nbsp;|&nbsp;
                🧑‍💻 <a href="https://github.com/MatheusFLB/glicoseando/" target="_blank">Source Code</a>
            </div>
            """,
            unsafe_allow_html=True
        )


# ==================== PONTO DE ENTRADA DA APLICAÇÃO ====================
# Verifica se este é o arquivo sendo executado (não um módulo importado)
if __name__ == "__main__":
    main()  # Executa a função principal
