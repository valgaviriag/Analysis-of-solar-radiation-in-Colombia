# ☀️ Solar Colombia | Radiation Dashboard

![alt text](image.png)

## 📌 Description
**Solar Colombia** is an interactive geospatial analysis platform designed to visualize and analyze solar radiation potential across the Colombian territory. Using historical data from the **IDEAM** station network, the project applies advanced interpolation algorithms (**Kriging**) to generate continuous radiation surfaces, allowing for the identification of areas with the highest suitability for photovoltaic energy projects.

## 🚀 Main Features
- **Interactive Heatmap**: Dynamic visualization of solar radiation (kWh/m²) across the country.
- **Kriging Interpolation**: Mathematical model (Ordinary Kriging - Spherical) applied over 8,000 points for superior territorial precision.
- **Multi-language Support**: Interface available in **English**, **Spanish**, and **German**.
- **Animation Mode**: Automatic playback of solar variability throughout the months of the year.
- **Geographic KPI Panel**:
  - **Solar Potential**: Automatic classification (Excellent, High, Moderate, Low).
  - **P90 Index**: Radiation guarantee exceeded by 90% of the territory.
  - **Regional Leader**: Dynamic identification of the department with the highest radiation levels.
- **Premium Design**: Modern dark mode interface with glassmorphism effects and responsive layout.

## 🛠️ Tech Stack
### Frontend
- **HTML5 / JavaScript (ES6+)**
- **Tailwind CSS**: Modern utility-first styling.
- **Plotly.js**: Rendering engine for the base map (Mapbox) and spatial data visualization.
- **FontAwesome**: Technical iconography.
- **Internationalization (i18n)**: Native implementation for dynamic language switching.

### Geostatistical Analysis & Backend
- **Python**: Data processing and geospatial modeling.
- **PyKrige**: Implementation of the Ordinary Kriging model.
- **GeoPandas & Shapely**: Processing of geometries and national geographic masks.
- **Pandas & NumPy**: Efficient manipulation of large volumes of meteorological data.

## 📂 Project Structure
- `index.html`: Main dashboard with multi-language support and visualization logic.
- `kriging_interpolation.py`: Python script to process CSV data and generate the interpolated grid.
- `radiation_data.csv`: Station data (Monthly radiation and annual average).
- `colombia.json`: National boundary GeoJSON for clipping the interpolation.
- `kriging_data.json`: Processed interpolation results for dashboard consumption.
- `convert_units.py`: Utility for unit normalization (Wh/m² to kWh/m²).

## 📊 Methodology
The radiation surface is generated using **Ordinary Kriging**, a geostatistical method that estimates values at unsampled points based on the spatial correlation of known data (stations).
1. **Cleaning**: IDEAM data is processed by removing null values and normalizing coordinates.
2. **Interpolation**: The spherical model is executed for each month of the year.
3. **Masking**: Results are filtered using Colombia's official polygon to avoid distortions in border and oceanic areas.

## ⚙️ Installation and Local Usage
1. Clone the repository.
2. Open `index.html` in a browser (using a local server like VS Code's *Live Server* is recommended to load JSON files correctly).
3. To update the data:
   - Install Python dependencies: `pip install pandas numpy pykrige geopandas shapely`
   - Run `python kriging_interpolation.py` to regenerate the data grid.

---
*Developed for renewable energy analysis in Colombia.*
