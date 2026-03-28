# ndvi-agriculture-change-analysis

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Streamlit App](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B.svg)](https://streamlit.io/)

> **Remote sensing interpretation | Geospatial data science | Earth observation**

A comprehensive **geospatial analysis dashboard** for detecting land-use changes, agricultural intensification, and environmental trends using 26 years of NDVI satellite data (2000–2026).

---

## 🎯 Overview

This project analyzes a time series of **NDVI (Normalized Difference Vegetation Index)** data from an agricultural area in Brazil using satellite imagery from NASA's MODIS sensor. The dashboard detects:

- ✅ **Deforestation and pasture-to-crop conversions**
- ✅ **Seasonal agricultural cycles** (single-crop, double-crop, etc.)
- ✅ **Agricultural intensification trends**
- ✅ **Temporal changes in vegetation dynamics**
- ✅ **Land-use classification periods** (2000–2002, 2003–2010, 2010–2026)

### Key Features

| Feature | Description |
|---------|-------------|
| 🗺️ **Interactive Map** | Folium-based visualization with polygon overlay and KPI metrics |
| 📈 **Time Series Analysis** | Raw + smoothed NDVI with peak detection and trend analysis |
| 🔍 **Change Detection** | Binary segmentation algorithm to identify structural breaks |
| 🌾 **Crop Classification** | Infers crop type (single, double, pasture, perennial) from seasonal patterns |
| 📊 **Annual Metrics** | Mean, max, min NDVI per year with trend visualization |
| 📅 **Temporal Classification** | Automated period classification reflecting agricultural evolution |
| ⚡ **Interactive Dashboard** | Streamlit web app with real-time analysis controls |

---

## 📊 Data Source

**MODIS NDVI data via AgroAPI (SATVeg)**

- **Satellite:** MODIS (Terra/Aqua)
- **Resolution:** 250m spatial × 8–16 day temporal
- **Period:** 2000–02-18 to 2026–02-10 (1,142 observations)
- **Provider:** Embrapa Informática Agropecuária (SATVeg - Sistema de Análise Temporal da Vegetação)

**Study Area:**
- Location: Brazil (latitude ~-13.5°, longitude ~-58.9°)
- Area: ~250 hectares (calculated from polygon)
- Coordinates: Polygon with 20 vertices

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.9+**
- **pip** or **conda** for package management

### Installation

1. **Clone the repository:**

```bash
git clone https://github.com/yourusername/glicoseando.git
cd glicoseando
```

2. **Create a virtual environment (recommended):**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

### Running the Dashboard

```bash
streamlit run streamlit_app.py
```

The application will open at `http://localhost:8501`

---

## 📁 Project Structure

```
glicoseando/
├── data/
│   ├── ndvi_request.json         # API request parameters
│   └── ndvi_timeseries.json      # NDVI time series data (1,144 observations)
│
├── src/
│   ├── __init__.py               # Package initialization
│   ├── data_processing.py        # Load & clean NDVI data
│   ├── polygon_processing.py     # Polygon geometry & area calculations
│   ├── ndvi_analysis.py          # Temporal analysis & metrics
│   ├── change_detection.py       # Change point detection (ruptures)
│   └── map_generator.py          # Folium interactive maps
│
├── outputs/
│   ├── figures/                  # Exported charts
│   └── maps/                     # Exported interactive maps (HTML)
│
├── streamlit_app.py              # Main dashboard application
├── requirements.txt              # Python dependencies
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

---

## 🔧 Module Description

### 1. `data_processing.py`

Handles loading and validating NDVI time series data from JSON format.

**Key Functions:**
- `load_ndvi_data()` - Parse JSON, create DataFrame, validate structure
- `clean_ndvi_data()` - Remove outliers and NaN values
- `get_data_summary()` - Generate descriptive statistics

### 2. `polygon_processing.py`

Manages geospatial polygon operations using GeoPandas and Shapely.

**Key Functions:**
- `parse_polygon_string()` - Convert API coordinates to tuples
- `create_geodataframe()` - Create GeoDataFrame from coordinates
- `calculate_area_hectares()` - Reproject to equal-area (EPSG:6933) and calculate
- `get_polygon_stats()` - Generate comprehensive polygon statistics

### 3. `ndvi_analysis.py`

Temporal analysis module for extracting seasonal patterns and trends.

**Key Functions:**
- `smooth_series()` - Rolling window or Savitzky-Golay filtering
- `identify_peaks()` - Detect vegetation peaks using scipy
- `extract_annual_metrics()` - Group by year, compute statistics
- `detect_seasonal_cycles()` - Infer crop type from cycle frequency
- `classify_periods()` - Categorize into 3 temporal periods
- `get_period_statistics()` - Per-period NDVI summaries

### 4. `change_detection.py`

Detects structural changes and estimates deforestation onset.

**Key Functions:**
- `detect_change_points()` - Binary segmentation (ruptures library)
- `estimate_deforestation_onset()` - Identify first major change
- `calculate_intensity_score()` - Compute agricultural intensification (0–1)
- `classify_change_severity()` - Rank changes as severe/moderate/minor

### 5. `map_generator.py`

Creates interactive visualizations using Folium.

**Key Functions:**
- `create_interactive_map()` - Generate Folium map with polygon
- `get_color_for_ndvi()` - NDVI-to-color mapping (brown → green)
- `create_ndvi_legend()` - Add color scale legend
- `create_full_featured_map()` - All-in-one map generation

### 6. `streamlit_app.py`

Main dashboard integrating all modules with interactive controls.

**Sections:**
- **KPI Metrics:** Area, mean NDVI, observation count
- **Geographic Map:** Folium visualization with polygon
- **Time Series:** Raw + smoothed NDVI with peak detection
- **Change Detection:** Breakpoints and deforestation onset
- **Period Classification:** Statistics by temporal period
- **Annual Trends:** Year-over-year NDVI evolution
- **Seasonal Analysis:** Crop type inference and cycle metrics
- **Detailed Stats:** Optional extended analysis

---

## 📊 Analysis Workflow

### 1. Data Loading
```python
from src.data_processing import load_ndvi_data
df = load_ndvi_data("data/ndvi_timeseries.json")
# Returns: DataFrame with 'date' and 'ndvi' columns
```

### 2. Polygon Processing
```python
from src.polygon_processing import (
    parse_polygon_string, create_geodataframe, calculate_area_hectares
)
coords = parse_polygon_string(request_data["poligono"])
gdf = create_geodataframe(coords)
area_ha = calculate_area_hectares(gdf)
```

### 3. Temporal Analysis
```python
from src.ndvi_analysis import extract_annual_metrics, detect_seasonal_cycles
annual_df = extract_annual_metrics(df)
cycles = detect_seasonal_cycles(df)
```

### 4. Change Detection
```python
from src.change_detection import detect_change_points, estimate_deforestation_onset
change_points = detect_change_points(df["ndvi"].values)
deforestation = estimate_deforestation_onset(df, change_points)
```

### 5. Visualization
```python
from src.map_generator import create_full_featured_map
m = create_full_featured_map(gdf, center, mean_ndvi, area_ha)
m.save("outputs/maps/analysis_map.html")
```

---

## 🧪 Testing & Validation

Quick validation tests:

```python
# Data integrity
df = load_ndvi_data("data/ndvi_timeseries.json")
assert len(df) == 1144
assert df["date"].min() == pd.Timestamp("2000-02-18")

# Polygon geometry
gdf = create_geodataframe(coords)
area = calculate_area_hectares(gdf)
assert 100 < area < 1000  # Reasonable area range

# Change detection
change_pts = detect_change_points(df["ndvi"].values)
assert 1 <= len(change_pts) <= 5  # Expect 1–5 breakpoints

# Analysis completeness
annual = extract_annual_metrics(df)
assert len(annual) == 26  # 26 years
assert annual["mean_ndvi"].notna().all()
```

---

## 📌 Key Findings & Interpretations

### Temporal Periods

**Period 1 (2000–2002): Transition**
- Irregular NDVI patterns
- Possible pastage-to-crop conversion
- Mean NDVI ~0.40–0.50

**Period 2 (2003–2010): Established Agriculture**
- Regular seasonal cycles
- Mean NDVI ~0.55–0.65
- Clear crop peaks and dormant phases

**Period 3 (2010–2026): Intensive Agriculture**
- High and frequent NDVI peaks (>0.85)
- Possible double-cropping system
- Mean NDVI ~0.70–0.75
- Consistent high productivity

### Seasonal Patterns

- **Cycles/Year:** Indicates single-crop, double-crop, or pasture systems
- **Cycle Duration:** Typical agricultural cycle ~6–8 months for single crops
- **Amplitude:** Range between dormant and peak vegetation

### Change Severity Levels

- **Severe (`> 0.15`):** Major vegetation loss (deforestation, abandonment)
- **Moderate (`0.05–0.15`):** Significant shift (land conversion)
- **Minor (`< 0.05`):** Subtle variation (management changes)
- **Gain (`> 0`):** NDVI increase (reforestation, intensification)

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Data Processing** | Pandas, NumPy | Time series manipulation |
| **Geospatial** | GeoPandas, Shapely | Polygon operations |
| **Analysis** | SciPy, ruptures | Temporal analysis, change detection |
| **Visualization** | Plotly, Folium | Interactive charts and maps |
| **Dashboard** | Streamlit | Web application interface |
| **Language** | Python 3.9+ | Core implementation |

---

## 📦 Dependencies

See `requirements.txt`:

```
pandas>=1.5.0
numpy>=1.23.0
geopandas>=0.12.0
shapely>=2.0.0
folium>=0.14.0
plotly>=5.14.0
ruptures>=1.1.8
streamlit>=1.28.0
pyproj>=3.5.0
scipy>=1.10.0
```

---

## 🌐 Deployment

### Local Development
```bash
streamlit run streamlit_app.py
```

### Streamlit Cloud
```bash
# Requires GitHub repository
# Visit: https://share.streamlit.io/
# Connect repo and deploy
```

### Docker (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "streamlit_app.py"]
```

---

## 📖 References

- **SATVeg System:** [Sistema de Análise Temporal da Vegetação](https://www.sativeg.cnptia.embrapa.br/)
- **AgroAPI:** Embrapa APIs for agricultural data
- **MODIS:** [NASA MODIS Instrument](https://modis.gsfc.nasa.gov/)
- **NDVI:** [Normalized Difference Vegetation Index](https://en.wikipedia.org/wiki/Normalized_difference_vegetation_index)
- **Ruptures:** [Time Series Change Point Detection](https://github.com/deepcharles/ruptures)

---

## 📝 License

This project is licensed under the **MIT License** — see LICENSE file for details.

---

## 👨‍💻 Author

**Data Science & Geospatial Analysis Team**

- Remote sensing interpretation
- Geospatial data science
- Agricultural monitoring

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📧 Support

For questions or issues:
- Open an issue on GitHub
- Contact: [your-email@example.com]

---

**Keywords:** `ndvi` | `agriculture` | `change-analysis` | `remote-sensing` | `geospatial` | `earth-observation` | `satellite-data` | `streamlit` | `geopython`

