"""
Polygon processing module for geospatial data handling.

This module handles parsing polygon coordinates, creating GeoDataFrames,
and calculating polygon area in hectares using proper projections.
"""

from typing import List, Optional, Tuple

import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon


def parse_polygon_string(poly_string: str) -> List[Tuple[float, float]]:
    """
    Parse polygon coordinates from API format string.

    Parse a space-separated string of longitude-latitude pairs
    separated by commas into a list of (lon, lat) tuples.

    Parameters
    ----------
    poly_string : str
        Polygon string in format: "lon1 lat1,lon2 lat2,..."
        Example: "-58.914 -13.507,-58.865 -13.513,..."

    Returns
    -------
    List[Tuple[float, float]]
        List of (longitude, latitude) tuples.

    Raises
    ------
    ValueError
        If the string format is invalid.
    """
    coordinates = []

    try:
        pairs = poly_string.split(",")
        for pair in pairs:
            lon_str, lat_str = pair.strip().split()
            coordinates.append((float(lon_str), float(lat_str)))
    except (ValueError, IndexError) as e:
        raise ValueError(
            f"Invalid polygon string format. Expected 'lon lat, lon lat, ...'. "
            f"Got: {poly_string[:50]}..."
        ) from e

    if len(coordinates) < 3:
        raise ValueError(
            f"Polygon must have at least 3 vertices, got {len(coordinates)}"
        )

    return coordinates


def create_geodataframe(
    coordinates: List[Tuple[float, float]]
) -> gpd.GeoDataFrame:
    """
    Create a GeoDataFrame from polygon coordinates.

    Parameters
    ----------
    coordinates : List[Tuple[float, float]]
        List of (longitude, latitude) tuples defining the polygon.

    Returns
    -------
    gpd.GeoDataFrame
        GeoDataFrame with a single polygon feature in EPSG:4326.

    Raises
    ------
    ValueError
        If coordinates are invalid.
    """
    if len(coordinates) < 3:
        raise ValueError("At least 3 coordinates are required for a polygon.")

    # Create Shapely Polygon (requires counter-clockwise or clockwise ordering)
    polygon = Polygon(coordinates)

    if not polygon.is_valid:
        raise ValueError("Invalid polygon geometry.")

    # Create GeoDataFrame with WGS84 projection
    gdf = gpd.GeoDataFrame(
        {"id": [1], "geometry": [polygon]}, crs="EPSG:4326"
    )

    return gdf


def calculate_area_hectares(gdf: gpd.GeoDataFrame) -> float:
    """
    Calculate polygon area in hectares using equal-area projection.

    Reprojects the GeoDataFrame to EPSG:6933 (South America Equidistant)
    which is an equal-area projection, then computes the area in square meters
    and converts to hectares (1 ha = 10000 m²).

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame containing polygon geometry.

    Returns
    -------
    float
        Area in hectares.

    Raises
    ------
    ValueError
        If the GeoDataFrame is empty or geometry is invalid.
    """
    if gdf.empty:
        raise ValueError("GeoDataFrame is empty.")

    if not gdf.geometry.is_valid.all():
        raise ValueError("Invalid geometry in GeoDataFrame.")

    # Reproject to equal-area projection for South America
    # EPSG:6933 - South America Equidistant (equal-area)
    gdf_projected = gdf.to_crs("EPSG:6933")

    # Calculate area in square meters
    area_m2 = gdf_projected.geometry.area.sum()

    # Convert to hectares (1 ha = 10000 m²)
    area_ha = area_m2 / 10000

    return area_ha


def get_polygon_center(gdf: gpd.GeoDataFrame) -> Tuple[float, float]:
    """
    Get the center coordinates of the polygon.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame containing polygon geometry.

    Returns
    -------
    Tuple[float, float]
        (latitude, longitude) of the polygon centroid.
    """
    centroid = gdf.geometry.unary_union.centroid
    return (centroid.y, centroid.x)  # Return as (lat, lon) for Folium


def get_polygon_bounds(gdf: gpd.GeoDataFrame) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """
    Get the bounding box of the polygon.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame containing polygon geometry.

    Returns
    -------
    Tuple[Tuple[float, float], Tuple[float, float]]
        ((min_lat, min_lon), (max_lat, max_lon))
    """
    bounds = gdf.total_bounds  # (minx, miny, maxx, maxy)
    return ((bounds[1], bounds[0]), (bounds[3], bounds[2]))


def get_polygon_stats(
    gdf: gpd.GeoDataFrame, mean_ndvi: Optional[float] = None
) -> dict:
    """
    Generate comprehensive statistics for the polygon.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame containing polygon geometry.
    mean_ndvi : float, optional
        Mean NDVI value for the polygon area.

    Returns
    -------
    dict
        Dictionary containing:
        - "area_ha": area in hectares
        - "center_coords": (lat, lon) centroid
        - "bounds": ((min_lat, min_lon), (max_lat, max_lon))
        - "mean_ndvi": mean NDVI value (if provided)
    """
    stats = {
        "area_ha": calculate_area_hectares(gdf),
        "center_coords": get_polygon_center(gdf),
        "bounds": get_polygon_bounds(gdf),
    }

    if mean_ndvi is not None:
        stats["mean_ndvi"] = mean_ndvi

    return stats


def polygon_to_geojson(gdf: gpd.GeoDataFrame) -> str:
    """
    Convert GeoDataFrame polygon to GeoJSON string.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame containing polygon geometry.

    Returns
    -------
    str
        GeoJSON representation of the polygon.
    """
    return gdf.to_json()
