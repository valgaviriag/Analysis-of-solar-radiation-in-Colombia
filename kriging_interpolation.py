import pandas as pd
import numpy as np
from pykrige.ok import OrdinaryKriging
import json
import os
import warnings

# Ignorar advertencias de matrices mal condicionadas
warnings.filterwarnings("ignore", category=UserWarning)

def perform_full_kriging(csv_path, output_json):
    print(f"Leyendo datos desde {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # Columnas a interpolar
    months = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC', 'Annual_Average']
    
    # Limpieza inicial: Coordenadas válidas
    df = df.dropna(subset=['Latitud', 'Longitud'])
    
    # Manejar duplicados: Si hay varias estaciones en la misma coordenada, promediamos sus valores
    # Esto evita el error de "Singular Matrix" en Kriging
    df_clean = df.groupby(['Latitud', 'Longitud'])[months].mean().reset_index()
    
    print(f"Datos limpios: {len(df_clean)} ubicaciones únicas.")
    
    # Definir límites de la cuadrícula (Colombia aproximado)
    # 50x65 es suficiente para una visualización fluida y ligera
    grid_lon = np.linspace(-82, -66, 50) 
    grid_lat = np.linspace(-4, 13, 65)
    
    results = {
        "lon": [round(x, 2) for x in grid_lon.tolist()],
        "lat": [round(y, 2) for y in grid_lat.tolist()],
        "data": {}
    }
    
    for month in months:
        if month not in df_clean.columns:
            continue
            
        # Filtrar NaNs para este mes específico
        valid_data = df_clean.dropna(subset=[month])
        if len(valid_data) < 3: # Necesitamos al menos 3 puntos para Kriging
            continue
            
        print(f"Interpolando {month}...")
        x = valid_data['Longitud'].values
        y = valid_data['Latitud'].values
        z = valid_data[month].values
        
        try:
            # Ordinary Kriging con modelo esférico (estándar de la industria)
            OK = OrdinaryKriging(
                x, y, z,
                variogram_model='spherical',
                verbose=False,
                enable_plotting=False
            )
            
            z_grid, ss_grid = OK.execute('grid', grid_lon, grid_lat)
            
            # Comprimir: Redondear a 2 decimales y convertir a lista
            # Reemplazar valores negativos (posibles en Kriging) por el mínimo real
            min_val = float(z.min())
            grid_final = np.round(z_grid.data, 2)
            grid_final[grid_final < min_val] = min_val
            
            results["data"][month] = grid_final.tolist()
        except Exception as e:
            print(f"Error en {month}: {e}")
            
    print(f"Guardando en {output_json}...")
    with open(output_json, 'w') as f:
        json.dump(results, f)
    
    size_kb = os.path.getsize(output_json) / 1024
    print(f"¡Kriging completado! Tamaño: {size_kb:.1f} KB")

if __name__ == "__main__":
    input_csv = '/home/vale/projects/Portofolio/Projects/Radiation/radiation_data.csv'
    output_js = '/home/vale/projects/Portofolio/Projects/Radiation/kriging_data.json'
    
    if os.path.exists(input_csv):
        perform_full_kriging(input_csv, output_js)
    else:
        print(f"Error: No se encontró el archivo {input_csv}")
