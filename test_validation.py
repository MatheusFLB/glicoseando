#!/usr/bin/env python3
"""
Validation script for the Glicoseando NDVI analysis project.

Run this after installing dependencies:
    pip install -r requirements.txt
    python test_validation.py
"""

import sys
import json
from pathlib import Path

def test_data_loading():
    """Test 1: Data Loading"""
    print("\n✓ Test 1: Loading NDVI Data...")
    try:
        from src.data_processing import load_ndvi_data

        df = load_ndvi_data("data/ndvi_timeseries.json")
        print(f"  ✅ Loaded {len(df)} observations")
        print(f"  ✅ Date range: {df['date'].min().date()} to {df['date'].max().date()}")
        print(f"  ✅ NDVI range: {df['ndvi'].min():.3f} to {df['ndvi'].max():.3f}")
        assert len(df) == 1144, "Expected 1144 observations"
        print("  ✅ Test passed!")
        return df
    except Exception as e:
        print(f"  ❌ Error: {e}")
        sys.exit(1)


def test_polygon_processing():
    """Test 2: Polygon Processing"""
    print("\n✓ Test 2: Polygon Processing...")
    try:
        from src.polygon_processing import (
            parse_polygon_string, create_geodataframe, calculate_area_hectares
        )

        with open("data/ndvi_request.json", "r") as f:
            request_data = json.load(f)

        coords = parse_polygon_string(request_data["poligono"])
        print(f"  ✅ Parsed {len(coords)} polygon vertices")

        gdf = create_geodataframe(coords)
        print(f"  ✅ Created GeoDataFrame with valid polygon")

        area_ha = calculate_area_hectares(gdf)
        print(f"  ✅ Calculated area: {area_ha:.2f} hectares")
        assert 100 < area_ha < 1000, "Area seems unreasonable"
        print("  ✅ Test passed!")
        return gdf, area_ha
    except Exception as e:
        print(f"  ❌ Error: {e}")
        sys.exit(1)


def test_ndvi_analysis(df):
    """Test 3: NDVI Analysis"""
    print("\n✓ Test 3: NDVI Analysis...")
    try:
        from src.ndvi_analysis import (
            smooth_series, extract_annual_metrics,
            detect_seasonal_cycles, classify_periods
        )

        smoothed = smooth_series(df["ndvi"], window=32)
        print(f"  ✅ Smoothed series (len={len(smoothed)})")

        annual = extract_annual_metrics(df)
        print(f"  ✅ Extracted annual metrics: {len(annual)} years")
        assert len(annual) == 26, "Expected 26 years"

        cycles = detect_seasonal_cycles(df)
        print(f"  ✅ Detected {cycles['cycles_per_year']:.2f} cycles/year")
        print(f"  ✅ Inferred crop type: {cycles['crop_type_inferred']}")

        df_periods = classify_periods(df)
        print(f"  ✅ Classified into periods: {df_periods['period'].nunique()} types")
        print("  ✅ Test passed!")
    except Exception as e:
        print(f"  ❌ Error: {e}")
        sys.exit(1)


def test_change_detection(df):
    """Test 4: Change Detection"""
    print("\n✓ Test 4: Change Detection...")
    try:
        from src.change_detection import (
            calculate_intensity_score, classify_change_severity
        )

        intensity = calculate_intensity_score(df)
        print(f"  ✅ Calculated intensity score: {intensity:.2%}")
        assert 0 <= intensity <= 1, "Intensity out of range"

        severity = classify_change_severity(0.2)
        print(f"  ✅ Classified severity (mag=0.2): {severity}")

        try:
            from src.change_detection import detect_change_points
            pts = detect_change_points(df["ndvi"].values, n_breakpoints=3)
            print(f"  ✅ Detected {len(pts)} change points")
        except ImportError:
            print("  ⚠️  ruptures not installed (optional)")

        print("  ✅ Test passed!")
    except Exception as e:
        print(f"  ❌ Error: {e}")
        sys.exit(1)


def test_map_generation(gdf, area_ha, df):
    """Test 5: Map Generation"""
    print("\n✓ Test 5: Map Generation...")
    try:
        from src.map_generator import (
            get_color_for_ndvi, create_interactive_map, get_polygon_center
        )

        color_low = get_color_for_ndvi(0.2)
        color_high = get_color_for_ndvi(0.9)
        print(f"  ✅ Color mapping: low={color_low}, high={color_high}")

        center = get_polygon_center(gdf)
        print(f"  ✅ Polygon center: {center}")

        m = create_interactive_map(gdf, center, df["ndvi"].mean(), area_ha)
        print(f"  ✅ Created Folium map object")
        print("  ✅ Test passed!")
    except Exception as e:
        print(f"  ❌ Error: {e}")
        sys.exit(1)


def main():
    """Run all validation tests"""
    print("=" * 70)
    print("🌍 GLICOSEANDO - NDVI Agricultural Change Analysis Validation")
    print("=" * 70)

    # Run tests
    df = test_data_loading()
    gdf, area_ha = test_polygon_processing()
    test_ndvi_analysis(df)
    test_change_detection(df)
    test_map_generation(gdf, area_ha, df)

    print("\n" + "=" * 70)
    print("✅ ALL VALIDATION TESTS PASSED!")
    print("=" * 70)

    print("\n🚀 Project is ready for deployment!")
    print("\nTo run the dashboard:")
    print("  $ streamlit run streamlit_app.py")

    print("\n📁 Project structure:")
    print("  src/")
    print("    ├── data_processing.py        (Load & clean NDVI data)")
    print("    ├── polygon_processing.py     (Polygon geometry & area)")
    print("    ├── ndvi_analysis.py          (Temporal analysis)")
    print("    ├── change_detection.py       (Change point detection)")
    print("    └── map_generator.py          (Interactive maps)")
    print("  streamlit_app.py               (Main dashboard)")
    print("  output/                        (Exported maps & figures)")
    print("  data/                          (Input data)")
    print("  requirements.txt               (Dependencies)")
    print("  README.md                      (Documentation)")


if __name__ == "__main__":
    main()
