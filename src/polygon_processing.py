"""
MÓDULO DE PROCESSAMENTO DE POLÍGONOS GEOESPACIAIS

Responsável por processar dados geométricos de polígonos, incluindo:
- Parsing de coordenadas em diferentes formatos
- Criação de estruturas geométricas (GeoDataFrames)
- Cálculo de área, centroide e outras propriedades
- Conversão entre sistemas de coordenadas

CONCEITOS IMPORTANTES:
- Coordenadas em WGS84 (EPSG:4326): latitude/longitude global
- Projeção EPSG:6933: projeção de igual-área para América do Sul (para cálculo de área)
- Polígono: sequência de coordenadas formando uma área fechada
"""

from typing import List, Optional, Tuple

import geopandas as gpd
from shapely.geometry import Polygon


# ==================== PARSING DE COORDENADAS ====================
def parse_polygon_string(poly_string: str) -> List[Tuple[float, float]]:
    """
    Analisa coordenadas de polígono de uma string no formato da API.

    Converte uma string de coordenadas do formato da API SATVeg
    (longitude latitude separados por espaço, pares separados por vírgula)
    em uma lista estruturada de tuplas (longitude, latitude).

    Parameters
    ----------
    poly_string : str
        String de polígono no formato: "lon1 lat1,lon2 lat2,lon3 lat3,..."
        Exemplo: "-58.914 -13.507,-58.865 -13.513,-58.900 -13.550"

    Returns
    -------
    List[Tuple[float, float]]
        Lista de tuplas (longitude, latitude).

    Raises
    ------
    ValueError
        Se o formato da string é inválido.

    Example
    -------
    >>> coords = parse_polygon_string("-58.914 -13.507,-58.865 -13.513,-58.900 -13.550")
    >>> print(coords)
    [(-58.914, -13.507), (-58.865, -13.513), (-58.900, -13.550)]
    """
    coordinates = []

    try:
        # Divide a string por vírgula para obter pares longitude latitude
        pairs = poly_string.split(",")
        for pair in pairs:
            # Divide cada par por espaço para obter longitude e latitude
            lon_str, lat_str = pair.strip().split()
            # Converte para float e adiciona à lista
            coordinates.append((float(lon_str), float(lat_str)))
    except (ValueError, IndexError) as e:
        raise ValueError(
            f"Invalid polygon string format. Expected 'lon lat, lon lat, ...'. "
            f"Got: {poly_string[:50]}..."
        ) from e

    # Valida se há pelo menos 3 vértices (mínimo para um polígono)
    if len(coordinates) < 3:
        raise ValueError(
            f"Polygon must have at least 3 vertices, got {len(coordinates)}"
        )

    return coordinates


# ==================== CRIAÇÃO DE GEODATAFRAMES ====================
def create_geodataframe(
    coordinates: List[Tuple[float, float]]
) -> gpd.GeoDataFrame:
    """
    Cria um GeoDataFrame a partir de coordenadas de polígono.

    Converte uma lista de coordenadas em um objeto geométrico (Polygon)
    e o encapsula em um GeoDataFrame com projeção WGS84 (EPSG:4326).

    Parameters
    ----------
    coordinates : List[Tuple[float, float]]
        Lista de tuplas (longitude, latitude) definindo o polígono.

    Returns
    -------
    gpd.GeoDataFrame
        GeoDataFrame com um polígono em EPSG:4326 (WGS84).

    Raises
    ------
    ValueError
        Se as coordenadas são inválidas ou o polígono é inválido.

    Example
    -------
    >>> coords = [(-58.914, -13.507), (-58.865, -13.513), (-58.900, -13.550)]
    >>> gdf = create_geodataframe(coords)
    >>> print(gdf.crs)
    EPSG:4326
    """
    if len(coordinates) < 3:
        raise ValueError("At least 3 coordinates are required for a polygon.")

    # Cria um polígono Shapely a partir das coordenadas
    polygon = Polygon(coordinates)

    # Valida se o polígono é válido geometricamente
    if not polygon.is_valid:
        raise ValueError("Invalid polygon geometry.")

    # Cria um GeoDataFrame com o polígono
    # CRS (Coordinate Reference System) = EPSG:4326 = WGS84 (sistema global)
    gdf = gpd.GeoDataFrame(
        {"id": [1], "geometry": [polygon]}, crs="EPSG:4326"
    )

    return gdf


# ==================== CÁLCULO DE ÁREA ====================
def calculate_area_hectares(gdf: gpd.GeoDataFrame) -> float:
    """
    Calcula a área do polígono em hectares usando projeção de igual-área.

    Para cálculo preciso de área, o polígono é reprojetado de WGS84
    para EPSG:6933 (projeção de igual-área para América do Sul).
    A área é calculada em m² e convertida para hectares.

    1 hectare = 10.000 m²

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame contendo geometria de polígono.

    Returns
    -------
    float
        Área em hectares.

    Raises
    ------
    ValueError
        Se o GeoDataFrame está vazio ou contém geometria inválida.

    Example
    -------
    >>> area_ha = calculate_area_hectares(gdf)
    >>> print(f"Área: {area_ha:.2f} hectares")
    """
    if gdf.empty:
        raise ValueError("GeoDataFrame is empty.")

    if not gdf.geometry.is_valid.all():
        raise ValueError("Invalid geometry in GeoDataFrame.")

    # Reprojetar para EPSG:6933 (South America Equidistant)
    # Esta é uma projeção de igual-área apropriada para cálculos precisos
    gdf_projected = gdf.to_crs("EPSG:6933")

    # Calcula a área em metros quadrados
    area_m2 = gdf_projected.geometry.area.sum()

    # Converte para hectares (1 ha = 10.000 m²)
    area_ha = area_m2 / 10000

    return area_ha


# ==================== OBTENÇÃO DE CENTROIDE ====================
def get_polygon_center(gdf: gpd.GeoDataFrame) -> Tuple[float, float]:
    """
    Obtém as coordenadas do centro (centroide) do polígono.

    Calcula o centroide geométrico do polígono, útil para
    centralizar o mapa na visualização.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame contendo geometria de polígono.

    Returns
    -------
    Tuple[float, float]
        (latitude, longitude) do centroide em WGS84.
        Nota: Folium espera (latitude, longitude), não (longitude, latitude)

    Example
    -------
    >>> center = get_polygon_center(gdf)
    >>> print(f"Centro: {center}")
    (-13.512, -58.893)
    """
    # Calcula o centroide (ponto central) da geometria
    centroid = gdf.geometry.unary_union.centroid
    # Retorna como (latitude, longitude) para Folium
    # (não como lon, lat que é o padrão geométrico)
    return (centroid.y, centroid.x)


# ==================== OBTENÇÃO DE BOUNDING BOX ====================
def get_polygon_bounds(gdf: gpd.GeoDataFrame) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """
    Obtém o bounding box (retângulo envolvente) do polígono.

    Útil para determinar os limites da área de interesse
    para zoomear o mapa corretamente.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame contendo geometria de polígono.

    Returns
    -------
    Tuple[Tuple[float, float], Tuple[float, float]]
        ((latitude_mínima, longitude_mínima), (latitude_máxima, longitude_máxima))

    Example
    -------
    >>> bounds = get_polygon_bounds(gdf)
    >>> print(f"Bounds: {bounds}")
    """
    # total_bounds retorna (minx, miny, maxx, maxy) = (min_lon, min_lat, max_lon, max_lat)
    bounds = gdf.total_bounds
    # Converte para ((min_lat, min_lon), (max_lat, max_lon))
    return ((bounds[1], bounds[0]), (bounds[3], bounds[2]))


# ==================== GERAÇÃO DE ESTATÍSTICAS ====================
def get_polygon_stats(
    gdf: gpd.GeoDataFrame, mean_ndvi: Optional[float] = None
) -> dict:
    """
    Gera estatísticas completas para o polígono.

    Compila informações geométricas e espectrais sobre a área de interesse.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame contendo geometria de polígono.
    mean_ndvi : float, optional
        Valor médio de NDVI para a área (se disponível).

    Returns
    -------
    dict
        Dicionário contendo:
        - "area_ha": área em hectares
        - "center_coords": (latitude, longitude) do centroide
        - "bounds": bounding box do polígono
        - "mean_ndvi": valor médio de NDVI (se fornecido)

    Example
    -------
    >>> stats = get_polygon_stats(gdf, mean_ndvi=0.65)
    >>> print(f"Área: {stats['area_ha']:.2f} ha")
    >>> print(f"NDVI médio: {stats['mean_ndvi']:.3f}")
    """
    stats = {
        "area_ha": calculate_area_hectares(gdf),
        "center_coords": get_polygon_center(gdf),
        "bounds": get_polygon_bounds(gdf),
    }

    # Adiciona NDVI médio se foi fornecido
    if mean_ndvi is not None:
        stats["mean_ndvi"] = mean_ndvi

    return stats


# ==================== CONVERSÃO PARA GEOJSON ====================
def polygon_to_geojson(gdf: gpd.GeoDataFrame) -> str:
    """
    Converte um GeoDataFrame com polígono para string GeoJSON.

    GeoJSON é um formato padrão para dados geoespaciais.
    Útil para visualização em bibliotecas como Folium ou Leaflet.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame contendo geometria de polígono.

    Returns
    -------
    str
        Representação GeoJSON do polígono como string JSON.

    Example
    -------
    >>> geojson_str = polygon_to_geojson(gdf)
    >>> print(geojson_str)
    """
    return gdf.to_json()
