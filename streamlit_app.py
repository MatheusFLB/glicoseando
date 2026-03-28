"""
Streamlit dashboard for NDVI agricultural change analysis.

This is the main application that integrates all modules to create
an interactive geospatial analysis dashboard.
"""

import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

from src.data_processing import load_ndvi_data
from src.polygon_processing import (
    parse_polygon_string,
    create_geodataframe,
    get_polygon_stats,
    get_polygon_center,
)
from src.ndvi_analysis import (
    smooth_series,
    identify_peaks,
    extract_annual_metrics,
    classify_periods,
    detect_seasonal_cycles,
    get_period_statistics,
    calculate_annual_change_rate,
)
from src.change_detection import (
    detect_change_points,
    estimate_deforestation_onset,
    calculate_intensity_score,
    classify_change_severity,
)
from src.map_generator import create_full_featured_map


# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="NDVI Agricultural Change Analysis",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==================== CUSTOM STYLING ====================
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
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

    # ==================== TITLE & HEADER ====================
    st.markdown("# 🌍 NDVI Agricultural Change Analysis Dashboard")
    st.markdown(
        """
        *Remote sensing interpretation | Geospatial data science | Earth observation*

        This dashboard analyzes a **26-year (2000–2026) satellite time series** of NDVI (Normalized Difference Vegetation Index)
        to detect land-use changes, agricultural intensification, and environmental trends in a Brazilian agricultural area.
        """
    )

    # ==================== SIDEBAR CONTROLS ====================
    with st.sidebar:
        st.header("⚙️ Analysis Controls")

        smoothing_window = st.slider(
            "NDVI Smoothing Window (observations)",
            min_value=4,
            max_value=64,
            value=32,
            step=4,
            help="Larger windows produce smoother curves but may hide short-term variations.",
        )

        show_peaks = st.checkbox(
            "Show NDVI Peaks", value=True,
            help="Highlight local maxima in the time series."
        )

        show_analysis_details = st.checkbox(
            "Show Detailed Analysis", value=False,
            help="Display additional statistical details."
        )

    # ==================== KPI METRICS ====================
    st.header("📊 Area Metrics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Area", f"{polygon_stats['area_ha']:.2f} ha")
    with col2:
        st.metric("Mean NDVI", f"{polygon_stats['mean_ndvi']:.3f}")
    with col3:
        st.metric("Period", "2000 – 2026")
    with col4:
        st.metric("Observations", f"{len(ndvi_df):,}")

    # ==================== INTERACTIVE MAP ====================
    st.header("🗺️ Geographic Location")
    center = get_polygon_center(gdf)
    m = create_full_featured_map(
        gdf,
        center,
        polygon_stats["mean_ndvi"],
        polygon_stats["area_ha"],
    )
    st.folium_static(m, width=1200, height=500)

    # ==================== NDVI TIME SERIES ====================
    st.header("📈 NDVI Time Series Analysis")

    # Prepare data for plotting
    ndvi_df_plot = ndvi_df.copy()
    ndvi_df_plot["smoothed"] = smooth_series(
        ndvi_df_plot["ndvi"], window=smoothing_window
    )

    # Identify peaks
    peaks_idx = identify_peaks(ndvi_df_plot["smoothed"], prominence=0.08)

    # Create Plotly figure
    fig = go.Figure()

    # Raw NDVI
    fig.add_trace(go.Scatter(
        x=ndvi_df_plot["date"],
        y=ndvi_df_plot["ndvi"],
        mode="lines",
        name="Raw NDVI",
        line=dict(color="lightblue", width=1),
        opacity=0.6,
    ))

    # Smoothed NDVI
    fig.add_trace(go.Scatter(
        x=ndvi_df_plot["date"],
        y=ndvi_df_plot["smoothed"],
        mode="lines",
        name="Smoothed NDVI",
        line=dict(color="darkblue", width=2),
    ))

    # Peaks
    if show_peaks and len(peaks_idx) > 0:
        fig.add_trace(go.Scatter(
            x=ndvi_df_plot.iloc[peaks_idx]["date"],
            y=ndvi_df_plot.iloc[peaks_idx]["smoothed"],
            mode="markers",
            name="Vegetation Peaks",
            marker=dict(size=8, color="red", symbol="star"),
        ))

    # Styling
    fig.update_layout(
        title="NDVI Time Series (2000–2026)",
        xaxis_title="Date",
        yaxis_title="NDVI Value",
        hovermode="x unified",
        template="plotly_white",
        height=500,
        margin=dict(l=50, r=50, t=50, b=50),
    )

    st.plotly_chart(fig, use_container_width=True)

    # ==================== CHANGE DETECTION ====================
    st.header("🔍 Change Point Detection")

    try:
        change_points = detect_change_points(
            ndvi_df["ndvi"].values, n_breakpoints=3, algo="binseg"
        )
        deforestation_info = estimate_deforestation_onset(ndvi_df, change_points)

        col1, col2, col3 = st.columns(3)

        with col1:
            if deforestation_info:
                st.metric(
                    "Change Onset Year",
                    deforestation_info["onset_year"]
                )
            else:
                st.metric("Change Onset Year", "–")

        with col2:
            if deforestation_info:
                magnitude = deforestation_info["magnitude"]
                severity = classify_change_severity(magnitude)
                st.metric("Change Severity", severity.title())
            else:
                st.metric("Change Severity", "–")

        with col3:
            intensity = calculate_intensity_score(ndvi_df)
            st.metric("Intensification Score", f"{intensity:.2%}")

        # Add vertical lines for change points in a new figure
        if len(change_points) > 0:
            fig_cp = go.Figure()

            fig_cp.add_trace(go.Scatter(
                x=ndvi_df["date"],
                y=ndvi_df["ndvi"],
                mode="lines",
                name="NDVI",
                line=dict(color="steelblue", width=2),
            ))

            for idx, cp in enumerate(change_points):
                if cp < len(ndvi_df):
                    cp_date = ndvi_df.iloc[cp]["date"]
                    fig_cp.add_vline(
                        x=cp_date,
                        line_dash="dash",
                        line_color="red",
                        annotation_text=f"Change {idx+1}" if idx == 0 else None,
                    )

            fig_cp.update_layout(
                title="Change Points Detected",
                xaxis_title="Date",
                yaxis_title="NDVI Value",
                hovermode="x unified",
                template="plotly_white",
                height=400,
            )

            st.plotly_chart(fig_cp, use_container_width=True)

    except ImportError:
        st.warning("Change detection requires ruptures package. Install with: pip install ruptures")

    # ==================== PERIODIC ANALYSIS ====================
    st.header("📅 Temporal Period Classification")

    # Classify periods
    ndvi_df_periods = classify_periods(ndvi_df)
    period_stats = get_period_statistics(ndvi_df)

    # Display period statistics
    period_cols = st.columns(len(period_stats))
    for col, (period_name, stats) in zip(period_cols, period_stats.items()):
        with col:
            st.markdown(f"### {period_name}")
            st.metric("Mean NDVI", f"{stats['mean']:.3f}")
            st.metric("Max NDVI", f"{stats['max']:.3f}")
            st.metric("Min NDVI", f"{stats['min']:.3f}")

    # ==================== ANNUAL METRICS ====================
    st.header("📋 Annual Metrics")

    annual_df = extract_annual_metrics(ndvi_df)

    # Annual trend chart
    fig_annual = go.Figure()

    fig_annual.add_trace(go.Scatter(
        x=annual_df["year"],
        y=annual_df["mean_ndvi"],
        mode="lines+markers",
        name="Mean NDVI",
        line=dict(color="darkgreen", width=3),
        marker=dict(size=6),
    ))

    fig_annual.add_trace(go.Scatter(
        x=annual_df["year"],
        y=annual_df["max_ndvi"],
        mode="lines",
        name="Max NDVI",
        line=dict(color="lightgreen", width=1, dash="dash"),
    ))

    fig_annual.add_trace(go.Scatter(
        x=annual_df["year"],
        y=annual_df["min_ndvi"],
        mode="lines",
        name="Min NDVI",
        line=dict(color="brown", width=1, dash="dash"),
    ))

    fig_annual.update_layout(
        title="Annual NDVI Trends",
        xaxis_title="Year",
        yaxis_title="NDVI Value",
        template="plotly_white",
        height=400,
    )

    st.plotly_chart(fig_annual, use_container_width=True)

    # Display annual metrics table
    st.dataframe(
        annual_df,
        use_container_width=True,
        hide_index=True,
    )

    # ==================== SEASONAL ANALYSIS ====================
    st.header("🌾 Seasonal Cycle Analysis")

    cycle_analysis = detect_seasonal_cycles(ndvi_df)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Cycles/Year", f"{cycle_analysis['cycles_per_year']:.2f}")
    with col2:
        st.metric("Cycle Duration", f"{cycle_analysis['cycle_duration_days']:.0f} days")
    with col3:
        st.metric("Crop Type Inferred", cycle_analysis['crop_type_inferred'].title())

    st.info(
        f"""
        **Interpretation:** The detected pattern suggests **{cycle_analysis['crop_type_inferred']}** agriculture.
        - **Single crop**: 0.5–1.5 cycles/year (annual harvest)
        - **Double crop**: 1.5–2.5 cycles/year (multiple harvests)
        - **Pasture**: <0.5 cycles/year (continuous grazing)
        - **Perennial**: >2.5 cycles/year (constant cultivation)
        """
    )

    # ==================== DETAILED ANALYSIS ====================
    if show_analysis_details:
        st.header("📊 Detailed Statistical Summary")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Data Overview")
            st.write(f"**Total Observations:** {len(ndvi_df):,}")
            st.write(f"**Date Range:** {ndvi_df['date'].min().date()} to {ndvi_df['date'].max().date()}")
            st.write(f"**Time Span:** {(ndvi_df['date'].max() - ndvi_df['date'].min()).days} days (~{(ndvi_df['date'].max() - ndvi_df['date'].min()).days / 365.25:.1f} years)")
            st.write(f"**Mean Interval:** ~{(ndvi_df['date'].diff().dt.days.mean()):.0f} days")

        with col2:
            st.subheader("NDVI Statistics")
            st.write(f"**Mean:** {ndvi_df['ndvi'].mean():.4f}")
            st.write(f"**Std Dev:** {ndvi_df['ndvi'].std():.4f}")
            st.write(f"**Min:** {ndvi_df['ndvi'].min():.4f}")
            st.write(f"**Max:** {ndvi_df['ndvi'].max():.4f}")
            st.write(f"**Annual Change Rate:** {calculate_annual_change_rate(annual_df):.4f}")

    # ==================== FOOTER ====================
    st.divider()
    st.markdown(
        """
        ---
        **Data Source:** MODIS NDVI (SATVeg API - EmbrapaAgricultural Informatics)
        **Resolution:** 250m spatial × 8–16 day temporal
        **Project:** NDVI Agricultural Change Analysis Dashboard
        **Terms:** Remote sensing interpretation | Geospatial data science | Earth observation
        """
    )


if __name__ == "__main__":
    main()
