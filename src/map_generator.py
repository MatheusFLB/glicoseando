"""
MÓDULO DE GERAÇÃO DE MAPAS INTERATIVOS

Responsável por criar visualizações cartográficas usando Folium:
- Mapas interativos com polígonos coloridos
- Coloração baseada em valores NDVI
- Adição de legendas e controles
- Marcadores e popups informativos
- Camadas base: Satellite (padrão) e OpenStreetMap

COLORIZAÇÃO POR NDVI:
A cor representa a saúde da vegetação:
- Marrom escuro (0.0-0.3): Vegetação muito baixa ou nenhuma
- Marrom claro (0.3-0.5): Vegetação esparsa
- Amarelo-verde (0.5-0.7): Vegetação moderada
- Verde claro (0.7-0.85): Vegetação alta
- Verde escuro (0.85-1.0): Vegetação densa (máximo vigor)
"""

from typing import Tuple

import folium
import geopandas as gpd
import numpy as np


# ==================== MAPEAMENTO DE CORES ====================
def get_color_for_ndvi(ndvi_value: float) -> str:
    """
    Mapeia um valor NDVI para uma cor em escala verde-marrom.

    Utiliza uma escala de 5 cores para representar diferentes níveis
    de vigor vegetativo, indo de marrom (baixa vegetação) a verde escuro (alta vegetação).

    Parameters
    ----------
    ndvi_value : float
        Valor NDVI (normalmente 0 a 1, mas pode estar fora desse intervalo).

    Returns
    -------
    str
        Código hexadecimal da cor (ex: "#8B4513", "#006400").

    Example
    -------
    >>> color_low = get_color_for_ndvi(0.2)
    >>> print(color_low)
    #8B4513
    >>> color_high = get_color_for_ndvi(0.9)
    >>> print(color_high)
    #006400
    """
    # Limita o valor NDVI ao intervalo [0, 1]
    # (alguns valores podem estar ligeiramente fora do intervalo)
    ndvi = np.clip(ndvi_value, 0, 1)

    # Seleciona cor baseado em intervalos de NDVI
    # Escala: verde (alta vegetação) a marrom (baixa vegetação)
    if ndvi < 0.3:
        # Marrom escuro - vegetação muito baixa
        return "#8B4513"
    elif ndvi < 0.5:
        # Marrom claro - vegetação esparsa
        return "#CD853F"
    elif ndvi < 0.7:
        # Amarelo-verde - vegetação moderada
        return "#ADFF2F"
    elif ndvi < 0.85:
        # Verde claro - vegetação alta
        return "#32CD32"
    else:
        # Verde escuro - vegetação densa (máximo vigor)
        return "#006400"


# ==================== CRIAÇÃO DE MAPA INTERATIVO ====================
def create_interactive_map(
    gdf: gpd.GeoDataFrame,
    center_coords: Tuple[float, float],
    mean_ndvi: float = 0.5,
    area_ha: float = 0.0,
) -> folium.Map:
    """
    Cria um mapa Folium interativo com o polígono e metadados.

    Gera um mapa personalizado com:
    - Polígono colorido de acordo com NDVI
    - Marcador no centroide
    - Popup com informações da área
    - Múltiplas camadas base (Satellite e OpenStreetMap)

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame contendo a geometria do polígono.
    center_coords : Tuple[float, float]
        (latitude, longitude) para centrar o mapa.
    mean_ndvi : float, default=0.5
        Valor médio de NDVI para codificação de cor.
    area_ha : float, default=0.0
        Área do polígono em hectares.

    Returns
    -------
    folium.Map
        Objeto Folium.Map pronto para renderização.

    Example
    -------
    >>> m = create_interactive_map(gdf, (center_lat, center_lon), mean_ndvi=0.65)
    >>> m.save('mapa.html')
    """
    # ==================== CRIAR MAPA BASE ====================
    # Cria um mapa Folium sem tiles inicialmente para adicionar camadas personalizadas
    m = folium.Map(
        location=center_coords,      # Coordenadas para centrar o mapa
        zoom_start=13,               # Nível inicial de zoom (13 = zoom médio)
        tiles=None,                  # Sem tiles padrão (camadas serão adicionadas manualmente)
        prefer_canvas=True,          # Melhor renderização em dispositivos móveis
    )

    # Faz o mapa responsivo (100% da largura/altura do container)
    m.get_root().width = "100%"
    m.get_root().height = "100%"

    # ==================== CAMADAS BASE ====================
    # Adiciona camada OpenStreetMap (mapa de ruas padrão)
    folium.TileLayer(
        tiles="OpenStreetMap",
        attr="© OpenStreetMap contributors",
        name="OpenStreetMap",
        overlay=False,               # Camada base, não sobreposição
        control=True,                # Aparece no controle de camadas
    ).add_to(m)

    # Adiciona camada de satélite (padrão - primeira camada visível)
    # Fonte: Esri World Imagery - imagens de satélite de alta resolução
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Tiles © Esri — Source: Esri, Maxar, Earthstar Geographics, and the GIS User Community",
        name="Satellite",
        overlay=False,               # Camada base, não sobreposição
        control=True,                # Aparece no controle de camadas
    ).add_to(m)

    # ==================== OBTER COR BASEADA EM NDVI ====================
    # Mapeia o valor médio de NDVI para uma cor
    polygon_color = get_color_for_ndvi(mean_ndvi)

    # ==================== ADICIONAR POLÍGONO AO MAPA ====================
    # Itera sobre as linhas do GeoDataFrame (geralmente uma)
    for _, row in gdf.iterrows():
        geometry = row.geometry

        # Processa apenas geometrias do tipo Polígono
        if geometry.geom_type == "Polygon":
            # Extrai as coordenadas do exterior do polígono
            # Converte de (longitude, latitude) para (latitude, longitude)
            # Folium espera (lat, lon), não (lon, lat)
            coords_latlon = [(lat, lon) for lon, lat in geometry.exterior.coords]

            # ==================== CRIAR POPUP COM INFORMAÇÕES ====================
            # Texto informativo que aparece ao clicar no polígono
            popup_text = f"""
            <b>Agricultural Area Analysis</b><br>
            Area: {area_ha:.2f} ha<br>
            Mean NDVI: {mean_ndvi:.3f}<br>
            Period: 2000 - 2026<br>
            <i>MODIS satellite data</i>
            """

            # ==================== ADICIONAR POLÍGONO ====================
            folium.Polygon(
                locations=coords_latlon,         # Coordenadas do polígono
                color=polygon_color,             # Cor da borda
                fill=True,                       # Preencher o polígono
                fillColor=polygon_color,         # Cor de preenchimento
                fillOpacity=0.6,                 # Transparência (0.6 = 60% opaco)
                weight=2,                        # Espessura da borda
                popup=folium.Popup(popup_text, max_width=250),  # Popup ao clicar
            ).add_to(m)

            # ==================== ADICIONAR MARCADOR NO CENTROIDE ====================
            # Marca o centro/centroide do polígono com um círculo azul
            folium.CircleMarker(
                location=center_coords,          # Coordenadas do centro
                radius=8,                        # Raio do círculo em pixels
                popup=f"Center ({center_coords[0]:.4f}, {center_coords[1]:.4f})",
                color="darkblue",                # Cor da borda
                fill=True,                       # Preencher o círculo
                fillColor="blue",                # Cor de preenchimento
                fillOpacity=0.7,                 # Transparência
                weight=2,                        # Espessura da borda
            ).add_to(m)

    return m


# ==================== CONTROLE DE CAMADAS ====================
def add_layer_control(m: folium.Map) -> folium.Map:
    """
    Adiciona controle interativo de camadas ao mapa Folium.

    Permite ao usuário ativar/desativar diferentes camadas do mapa,
    incluindo as camadas base (Satellite e OpenStreetMap).

    Parameters
    ----------
    m : folium.Map
        Objeto Folium.Map.

    Returns
    -------
    folium.Map
        Mesmo mapa com controle de camadas adicionado.
    """
    folium.LayerControl().add_to(m)
    return m


# ==================== CRIAR LEGENDA NDVI ====================
def create_ndvi_legend(m: folium.Map) -> folium.Map:
    """
    Adiciona uma legenda NDVI visual ao mapa.

    Mostra os intervalo de cores e seus significados:
    cores, valores de NDVI e interpretação de vegetação.

    Parameters
    ----------
    m : folium.Map
        Objeto Folium.Map.

    Returns
    -------
    folium.Map
        Mesmo mapa com legenda adicionada.
    """
    # HTML da legenda com estilo CSS personalizado
    legend_html = """
    <div style="position: absolute;
             top: 10px; left: 10px; width: 220px;
             background-color: white;
             border: 2px solid grey;
             z-index: 9999;
             font-size: 14px;
             padding: 10px;
             border-radius: 5px;
             box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
        <b>NDVI Classification</b><br>
        <i style="background: #8B4513; width: 18px; height: 18px;
                  display: inline-block; border: 1px solid black;"></i>
        Low vegetation (0.0–0.3)<br>
        <i style="background: #CD853F; width: 18px; height: 18px;
                  display: inline-block; border: 1px solid black;"></i>
        Sparse vegetation (0.3–0.5)<br>
        <i style="background: #ADFF2F; width: 18px; height: 18px;
                  display: inline-block; border: 1px solid black;"></i>
        Moderate vegetation (0.5–0.7)<br>
        <i style="background: #32CD32; width: 18px; height: 18px;
                  display: inline-block; border: 1px solid black;"></i>
        High vegetation (0.7–0.85)<br>
        <i style="background: #006400; width: 18px; height: 18px;
                  display: inline-block; border: 1px solid black;"></i>
        Dense vegetation (0.85–1.0)<br>
        <br>
        <small><i>Data: MODIS NDVI (2000–2026)</i></small>
    </div>
    """
    # Adiciona a legenda como elemento HTML ao mapa
    m.get_root().html.add_child(folium.Element(legend_html))
    return m


# ==================== CRIAR MAPA COM TODOS OS RECURSOS ====================
def create_full_featured_map(
    gdf: gpd.GeoDataFrame,
    center_coords: Tuple[float, float],
    mean_ndvi: float,
    area_ha: float,
    include_legend: bool = False,
) -> folium.Map:
    """
    Cria um mapa interativo completo com todos os recursos.

    Combina todas as funções anteriores para criar um mapa
    totalmente funcional e visualmente informativo.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame com geometria do polígono.
    center_coords : Tuple[float, float]
        (latitude, longitude) para centrar o mapa.
    mean_ndvi : float
        Valor médio de NDVI.
    area_ha : float
        Área em hectares.
    include_legend : bool, default=False
        Se False, a legenda é mostrada fora do mapa (no dashboard).
        Se True, inclui legenda no arquivo do mapa.

    Returns
    -------
    folium.Map
        Mapa interativo completo.

    Example
    -------
    >>> m = create_full_featured_map(gdf, center, 0.65, 150.5)
    >>> m.save('complete_map.html')
    """
    # ==================== CRIAR MAPA BASE COM POLÍGONO ====================
    m = create_interactive_map(gdf, center_coords, mean_ndvi, area_ha)

    # ==================== ADICIONAR RECURSOS ====================
    # Controle de camadas (permite ativar/desativar camadas)
    m = add_layer_control(m)

    # Adiciona legenda somente se solicitado
    # (geralmente a legenda está no dashboard, não no mapa)
    if include_legend:
        m = create_ndvi_legend(m)

    return m