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
    
    months = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC', 'Annual_Average']
    df = df.dropna(subset=['Latitud', 'Longitud'])
    df_clean = df.groupby(['Latitud', 'Longitud'])[months].mean().reset_index()
    
    # Increase resolution (80x100 to balance detail/weight - Total 8,000 points)
    grid_lon = np.linspace(-82, -66, 80) 
    grid_lat = np.linspace(-4, 13, 100)
    
    results = {
        "lon": [round(x, 3) for x in grid_lon.tolist()],
        "lat": [round(y, 3) for y in grid_lat.tolist()],
        "data": {},
        "mask": [] # We will store a binary matrix (1 inside, 0 outside)
    }
    
    # 1. Calculate Mask (Points inside Colombia)
    print("Calculating clipping mask...")
    mask_grid = np.zeros((len(grid_lat), len(grid_lon)), dtype=int)
    for i, lat in enumerate(grid_lat):
        for j, lon in enumerate(grid_lon):
            if colombia_geom.contains(Point(lon, lat)):
                mask_grid[i, j] = 1
    
    results["mask"] = mask_grid.tolist()
    
    # 2. Execute Kriging for each month
    for month in months:
        if month not in df_clean.columns: continue
        valid_data = df_clean.dropna(subset=[month])
        if len(valid_data) < 3: continue
            
        print(f"Interpolating {month}...")
        x = valid_data['Longitud'].values
        y = valid_data['Latitud'].values
        z = valid_data[month].values
        
        try:
            OK = OrdinaryKriging(x, y, z, variogram_model='spherical')
            z_grid, _ = OK.execute('grid', grid_lon, grid_lat)
            
            # Apply mask and round
            grid_final = np.round(z_grid.data, 2)
            # Outside points are set to null to reduce weight and visibility
            # We'll use None in Python so it becomes null in JSON
            masked_data = []
            for i in range(len(grid_lat)):
                row = []
                for j in range(len(grid_lon)):
                    if mask_grid[i, j] == 1:
                        val = grid_final[i, j]
                        if val < z.min(): val = z.min()
                        row.append(float(val))
                    else:
                        row.append(None)
                masked_data.append(row)
            
            results["data"][month] = masked_data
        except Exception as e:
            print(f"Error in {month}: {e}")
            
    print(f"Saving to {output_json}...")
    with open(output_json, 'w') as f:
        # Use compact separators to reduce JSON weight
        json.dump(results, f, separators=(',', ':'))
    
    print(f"Enhanced Kriging completed! Size: {os.path.getsize(output_json)/1024:.1f} KB")

if __name__ == "__main__":
    input_csv = '/home/vale/projects/Portofolio/Projects/Radiation/radiation_data.csv'
    input_geo = '/home/vale/projects/Portofolio/Projects/Radiation/colombia.json'
    output_js = '/home/vale/projects/Portofolio/Projects/Radiation/kriging_data.json'
    
    if os.path.exists(input_csv) and os.path.exists(input_geo):
        perform_enhanced_kriging(input_csv, input_geo, output_js)
    else:
        print("Missing required files.")
