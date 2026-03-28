"""
Glicoseando: NDVI Agricultural Change Analysis Dashboard

A comprehensive geospatial analysis tool for detecting land-use changes
and agricultural intensification using NDVI satellite data (2000-2026).

Modules:
    - data_processing: Load and process NDVI time series data
    - polygon_processing: Handle geospatial polygon operations
    - ndvi_analysis: Analyze temporal NDVI patterns
    - change_detection: Detect land-use changes and deforestation
    - map_generator: Create interactive visualizations
"""

__version__ = "0.1.0"
__author__ = "Data Science Team"

from .data_processing import load_ndvi_data, clean_ndvi_data
from .polygon_processing import (
    parse_polygon_string,
    create_geodataframe,
    calculate_area_hectares,
    get_polygon_stats,
)

__all__ = [
    "load_ndvi_data",
    "clean_ndvi_data",
    "parse_polygon_string",
    "create_geodataframe",
    "calculate_area_hectares",
    "get_polygon_stats",
]
