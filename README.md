# 🛰️ Glicoseando — NDVI Time Series Analysis for Precision Agriculture

## 🌐 Live Dashboard 👉 [![Streamlit App](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B.svg)](https://glicoseando.streamlit.app/)

> precision-agriculture | NDVI | remote-sensing | geospatial | earth-observation | streamlit

This project delivers an **end-to-end geospatial analysis pipeline**, transforming satellite-derived NDVI data into an **interactive dashboard for vegetation monitoring and agricultural insights**.

Built to showcase real-world skills in:

* geospatial data processing
* remote sensing analysis
* time series modeling
* interactive data visualization
* delivery of decision-ready insights

---

## 🎯 Project Goal

Develop an interactive solution to **analyze vegetation dynamics over time** using satellite data, enabling users to:

* monitor vegetation health
* identify seasonal patterns
* detect peak productivity periods
* explore long-term trends (26 years)

This type of solution is directly applicable to:

* 🌾 precision agriculture
* 🌍 environmental monitoring
* 📊 geospatial BI dashboards
* 🛰️ earth observation analytics

---

## 📦 Data Source

The data used in this project is obtained directly from the SATVeg (Vegetation Temporal Analysis System), developed by Embrapa, through its API and integrated with the Brazil Data Cube—an initiative by the National Institute for Space Research (INPE).

This integration enables direct access to satellite-based time series, particularly from Sentinel-2 and MODIS (Terra/Aqua), significantly enhancing capabilities for environmental analysis, agricultural monitoring, and land-use insights across Brazil.

* 📊 **NDVI Data:** Retrieved via SATVeg API (Embrapa)
* 📡 **Satellites:** MODIS (Terra/Aqua) + Sentinel-2
* 📏 **Resolution:** 250 m spatial × 8–16 days temporal
* 🗓️ **Period:** February 18, 2000 – February 10, 2026 (1,142+ observations)
* 🌎 **Provider:** Embrapa Agricultural Informatics (SATVeg)
* 🔗 **Integration:** Brazil Data Cube (INPE)

---

## 🧭 Solution Flow

* 📥 Collect NDVI time series via the SATVeg API (Embrapa), integrated with Brazil Data Cube (INPE)
* 🧹 Clean, validate, and standardize temporal data for consistency
* 📊 Structure time series for analytical processing
* 📈 Detect vegetation peaks using signal processing techniques (SciPy)
* 🗺️ Generate interactive spatial visualizations from geospatial data
* 🌐 Deliver insights through an interactive Streamlit dashboard

---

## 📊 What This Project Delivers

* ✅ 26-year NDVI time series analysis (2000–2026)
* ✅ Automated peak detection (vegetation cycles)
* ✅ Annual NDVI metrics (min / mean / max)
* ✅ Interactive map with NDVI-based color scaling
* ✅ Temporal exploration with zoom and filters
* ✅ Bilingual interface (PT / EN)

---

## 🗺️ Dashboard Features

* 📍 Interactive map with NDVI visualization
* 📈 Time series with detected peaks
* 📊 Annual trend analysis
* 🎛️ Time filtering and zoom
* 🌍 Language switch (Portuguese / English)

---

## 🧰 Tech Stack

* 🐍 Python — main language and scripts for the data pipeline and app
* 📊 Pandas / NumPy — time series data manipulation and processing
* 🧭 GeoPandas / Shapely — geospatial processing and polygon operations
* 📈 SciPy — peak detection and analytical computations
* 🗺️ Plotly, Folium — interactive charts and map visualizations
* 🌐 Streamlit — web-based dashboard interface

---

## 💼 Real-World Applications

This project reflects scenarios commonly found in:

* agricultural monitoring systems
* satellite data analytics platforms
* environmental intelligence tools
* geospatial consulting projects

---

## ⚙️ Run Locally

```bash
git clone https://github.com/yourusername/glicoseando.git
cd glicoseando

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run streamlit_app.py
```

---

## 👤 Author

#### Developed by [**Matheus Bissoli**](https://matheusflb.github.io/)

- 💼 [LinkedIn](https://www.linkedin.com/in/matheusbissoli/)
