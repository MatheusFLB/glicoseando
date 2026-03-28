"""
Map generation module for interactive geospatial visualization.

This module creates interactive maps using Folium to visualize
polygon geometry and NDVI statistics.
"""

from pathlib import Path
from typing import Optional, Tuple

import folium
import geopandas as gpd
import numpy as np
from folium import plugins


def get_color_for_ndvi(ndvi_value: float) -> str:
    """
    Get a color representing NDVI value on a green to brown scale.

    Parameters
    ----------
    ndvi_value : float
        NDVI value (typically 0 to 1, but can be outside range).

    Returns
    -------
    str
        Hex color code.
    """
    # Clamp NDVI to [0, 1]
    ndvi = np.clip(ndvi_value, 0, 1)

    # Green (high vegetation) to brown (low vegetation) gradient
    if ndvi < 0.3:
        # Dark brown
        return "#8B4513"
    elif ndvi < 0.5:
        # Brown to tan
        return "#CD853F"
    elif ndvi < 0.7:
        # Tan to yellow-green
        return "#ADFF2F"
    elif ndvi < 0.85:
        # Yellow-green to green
        return "#32CD32"
    else:
        # Dark green (high vegetation)
        return "#006400"


def create_interactive_map(
    gdf: gpd.GeoDataFrame,
    center_coords: Tuple[float, float],
    mean_ndvi: float = 0.5,
    area_ha: float = 0.0,
) -> folium.Map:
    """
    Create an interactive Folium map with the polygon and metadata.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame containing the polygon geometry.
    center_coords : Tuple[float, float]
        (latitude, longitude) to center the map.
    mean_ndvi : float, default=0.5
        Mean NDVI value for color coding.
    area_ha : float, default=0.0
        Area of polygon in hectares.

    Returns
    -------
    folium.Map
        Folium Map object ready for rendering.
    """
    # Create base map
    m = folium.Map(
        location=center_coords,
        zoom_start=13,
        tiles="OpenStreetMap",
    )

    # Get color based on NDVI
    polygon_color = get_color_for_ndvi(mean_ndvi)

    # Add polygon to map
    for idx, row in gdf.iterrows():
        geometry = row.geometry

        # Extract coordinates
        if geometry.geom_type == "Polygon":
            coords = list(geometry.exterior.coords)
            # Convert to [lat, lon] format for Folium
            coords_latlon = [(lat, lon) for lon, lat in coords]

            # Create popup text
            popup_text = f"""
            <b>Agricultural Area Analysis</b><br>
            Area: {area_ha:.2f} ha<br>
            Mean NDVI: {mean_ndvi:.3f}<br>
            Period: 2000 - 2026<br>
            <i>MODIS satellite data</i>
            """

            # Add polygon
            folium.Polygon(
                locations=coords_latlon,
                color=polygon_color,
                fill=True,
                fillColor=polygon_color,
                fillOpacity=0.6,
                weight=2,
                popup=folium.Popup(popup_text, max_width=250),
            ).add_to(m)

            # Add centroid marker
            folium.CircleMarker(
                location=center_coords,
                radius=8,
                popup=f"Center ({center_coords[0]:.4f}, {center_coords[1]:.4f})",
                color="darkblue",
                fill=True,
                fillColor="blue",
                fillOpacity=0.7,
                weight=2,
            ).add_to(m)

    return m


def add_layer_control(m: folium.Map) -> folium.Map:
    """
    Add layer control to the Folium map.

    Parameters
    ----------
    m : folium.Map
        Folium map object.

    Returns
    -------
    folium.Map
        Map with layer control added.
    """
    folium.LayerControl().add_to(m)
    return m


def add_scale(m: folium.Map) -> folium.Map:
    """
    Add a scale bar to the Folium map.

    Parameters
    ----------
    m : folium.Map
        Folium map object.

    Returns
    -------
    folium.Map
        Map with scale bar added.
    """
    from folium.plugins import Fullscreen
    Fullscreen(
        position="topright",
        force_separate_button=True,
    ).add_to(m)
    return m


def create_ndvi_legend(m: folium.Map) -> folium.Map:
    """
    Add an NDVI value legend to the map.

    Parameters
    ----------
    m : folium.Map
        Folium map object.

    Returns
    -------
    folium.Map
        Map with legend added.
    """
    legend_html = """
    <div style="position: fixed;
             bottom: 50px; left: 50px; width: 220px; height: 200px;
             background-color: white; border:2px solid grey; z-index:9999;
             font-size:14px; padding: 10px">
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
    m.get_root().html.add_child(folium.Element(legend_html))
    return m


def save_map(m: folium.Map, filepath: str | Path) -> None:
    """
    Save Folium map to HTML file.

    Parameters
    ----------
    m : folium.Map
        Folium map object.
    filepath : str or Path
        Path where the HTML file will be saved.
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    m.save(str(filepath))
    print(f"Map saved to: {filepath}")


def create_full_featured_map(
    gdf: gpd.GeoDataFrame,
    center_coords: Tuple[float, float],
    mean_ndvi: float,
    area_ha: float,
    save_path: Optional[str | Path] = None,
) -> folium.Map:
    """
    Create a complete interactive map with all features.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame with polygon geometry.
    center_coords : Tuple[float, float]
        (latitude, longitude) map center.
    mean_ndvi : float
        Mean NDVI value.
    area_ha : float
        Area in hectares.
    save_path : str or Path, optional
        If provided, saves the map to this path.

    Returns
    -------
    folium.Map
        Complete interactive map.
    """
    # Create base map
    m = create_interactive_map(gdf, center_coords, mean_ndvi, area_ha)

    # Add features
    m = add_layer_control(m)
    m = create_ndvi_legend(m)

    # Save if path provided
    if save_path:
        save_map(m, save_path)

    return m
