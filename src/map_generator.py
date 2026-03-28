"""
Map generation module for interactive geospatial visualization.

This module creates interactive maps using Folium to visualize
polygon geometry and NDVI statistics.
"""

from typing import Tuple

import folium
import geopandas as gpd
import numpy as np


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
    # Create base map with responsive sizing
    m = folium.Map(
        location=center_coords,
        zoom_start=13,
        tiles="OpenStreetMap",
        prefer_canvas=True,  # Better rendering for mobile
    )

    # Make the map container responsive
    m.get_root().width = "100%"
    m.get_root().height = "100%"

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
    m.get_root().html.add_child(folium.Element(legend_html))
    return m


def create_full_featured_map(
    gdf: gpd.GeoDataFrame,
    center_coords: Tuple[float, float],
    mean_ndvi: float,
    area_ha: float,
    include_legend: bool = False,
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
    include_legend : bool, default=False
        If False, legend is shown outside the map (in dashboard).

    Returns
    -------
    folium.Map
        Complete interactive map.
    """
    # Create base map
    m = create_interactive_map(gdf, center_coords, mean_ndvi, area_ha)

    # Add features
    m = add_layer_control(m)

    # Only include legend if specified (for standalone map files)
    if include_legend:
        m = create_ndvi_legend(m)

    return m
