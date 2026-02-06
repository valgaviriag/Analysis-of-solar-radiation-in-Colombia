import pandas as pd
import numpy as np
from pykrige.ok import OrdinaryKriging
import json
import os
import warnings
from shapely.geometry import shape, Point
import geopandas as gpd

# Ignore warnings
warnings.filterwarnings("ignore", category=UserWarning)

def perform_enhanced_kriging(csv_path, geojson_path, output_json):
    print(f"Reading data from {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # Load Colombia GeoJSON for clipping
    print(f"Loading geographic mask from {geojson_path}...")
    colombia_gdf = gpd.read_file(geojson_path)
    colombia_geom = colombia_gdf.geometry.union_all() # Merge parts if multipolygon
    
    months = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC', 'Annual']
    # Mapping CSV columns to desired keys
    column_mapping = {
        'Annual_Average': 'Annual',
        'Estacion': 'name',
        'Departamento': 'dept',
        'Latitud': 'lat',
        'Longitud': 'lon'
    }
    
    # Pre-process stations data (replaces parseCSV in JS)
    print("Processing stations data...")
    stations_df = df.copy()
    # Ensure consistent column naming
    for col in df.columns:
        if col in column_mapping:
            stations_df = stations_df.rename(columns={col: column_mapping[col]})
    
    # Fill missing values and ensure numeric
    for m in months:
        if m in stations_df.columns:
            stations_df[m] = pd.to_numeric(stations_df[m].toString().replace(',', '.'), errors='coerce') if hasattr(stations_df[m], 'str') else stations_df[m]
        elif 'Annual_Average' in df.columns and m == 'Annual':
            stations_df[m] = pd.to_numeric(df['Annual_Average'].toString().replace(',', '.'), errors='coerce') if hasattr(df['Annual_Average'], 'str') else df['Annual_Average']

    stations_list = []
    for _, row in stations_df.iterrows():
        station = {
            "name": str(row.get('name', 'Unnamed')),
            "dept": str(row.get('dept', 'N/A')),
            "lat": float(row['lat']),
            "lon": float(row['lon'])
        }
        for m in months:
            val = row.get(m, np.nan)
            station[m] = float(val) if not np.isnan(val) else 0.0
        stations_list.append(station)

    # Increase resolution (80x100 to balance detail/weight - Total 8,000 points)
    grid_lon = np.linspace(-82, -66, 80) 
    grid_lat = np.linspace(-4, 13, 100)
    
    dashboard_data = {
        "months": months,
        "stations": stations_list,
        "interpolation": {},
        "stats": {}
    }
    
    # 1. Calculate Mask (Points inside Colombia)
    print("Calculating clipping mask...")
    mask_grid = np.zeros((len(grid_lat), len(grid_lon)), dtype=int)
    for i, lat in enumerate(grid_lat):
        for j, lon in enumerate(grid_lon):
            if colombia_geom.contains(Point(lon, lat)):
                mask_grid[i, j] = 1
    
    # 2. Execute Kriging and Stats for each month
    for month in months:
        csv_month_col = 'Annual_Average' if month == 'Annual' else month
        if csv_month_col not in df.columns: 
            print(f"Skipping {month}, column {csv_month_col} not found.")
            continue
            
        valid_data = df.dropna(subset=['Latitud', 'Longitud', csv_month_col])
        if len(valid_data) < 3: continue
            
        print(f"Processing {month}...")
        x = valid_data['Longitud'].values
        y = valid_data['Latitud'].values
        z = valid_data[csv_month_col].values
        
        try:
            # Kriging
            OK = OrdinaryKriging(x, y, z, variogram_model='spherical')
            z_grid, _ = OK.execute('grid', grid_lon, grid_lat)
            
            # Apply mask and extract flattened data
            flat_lats = []
            flat_lons = []
            flat_z = []
            
            grid_values = z_grid.data
            for i in range(len(grid_lat)):
                for j in range(len(grid_lon)):
                    if mask_grid[i, j] == 1:
                        val = float(grid_values[i][j])
                        if val < z.min(): val = z.min()
                        flat_lats.append(round(float(grid_lat[i]), 3))
                        flat_lons.append(round(float(grid_lon[j]), 3))
                        flat_z.append(round(val, 2))
            
            dashboard_data["interpolation"][month] = {
                "lat": flat_lats,
                "lon": flat_lons,
                "z": flat_z
            }
            
            # Stats calculation (replaces updateStats logic in JS)
            if flat_z:
                sorted_z = sorted(flat_z)
                mean_val = sum(flat_z) / len(flat_z)
                max_val = sorted_z[-1]
                min_val = sorted_z[0]
                p90_val = sorted_z[int(len(sorted_z) * 0.1)]
                
                # Potential level
                if mean_val > 5.5: potential = 'Excelente'
                elif mean_val > 4.5: potential = 'Alto'
                elif mean_val > 3.5: potential = 'Moderado'
                else: potential = 'Bajo'
                
                # Regional leader
                leader_dept = "N/A"
                max_station_val = -1
                for s in stations_list:
                    if s[month] > max_station_val:
                        max_station_val = s[month]
                        leader_dept = s['dept']
                
                dashboard_data["stats"][month] = {
                    "mean": round(mean_val, 2),
                    "max": round(max_val, 2),
                    "min": round(min_val, 2),
                    "p90": round(p90_val, 2),
                    "potential": potential,
                    "leader": {"dept": leader_dept, "val": round(max_station_val, 2)}
                }
                
        except Exception as e:
            print(f"Error in {month}: {e}")
            import traceback
            traceback.print_exc()
            
    print(f"Saving to {output_json}...")
    with open(output_json, 'w') as f:
        json.dump(dashboard_data, f, separators=(',', ':'))
    
    print(f"Processing completed! Size: {os.path.getsize(output_json)/1024:.1f} KB")

if __name__ == "__main__":
    input_csv = '/home/vale/projects/Portofolio/Projects/Radiation/radiation_data.csv'
    input_geo = '/home/vale/projects/Portofolio/Projects/Radiation/colombia.json'
    output_js = '/home/vale/projects/Portofolio/Projects/Radiation/dashboard_data.json'
    
    if os.path.exists(input_csv) and os.path.exists(input_geo):
        perform_enhanced_kriging(input_csv, input_geo, output_js)
    else:
        print("Missing required files.")
