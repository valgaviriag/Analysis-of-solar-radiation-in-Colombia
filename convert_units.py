import csv
import os

input_file = '/home/vale/projects/Portofolio/Projects/Radiation/radiation_data.csv'
output_file = '/home/vale/projects/Portofolio/Projects/Radiation/radiation_data_kwh.csv'

# Backup original if not already backed up
backup_file = input_file + '.bak'
if not os.path.exists(backup_file):
    os.rename(input_file, backup_file)
    input_source = backup_file
else:
    input_source = backup_file

with open(input_source, mode='r', encoding='utf-8') as infile:
    reader = csv.reader(infile)
    headers = next(reader)
    
    # Identify indices
    # ENE is index 8, DIC is index 19
    # Annual_Average is index 24
    
    with open(input_file, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(headers)
        
        for row in reader:
            if not row:
                continue
            
            new_row = list(row)
            try:
                # Convert monthly values (indices 8 to 19)
                for i in range(8, 20):
                    if new_row[i]:
                        new_row[i] = str(round(float(new_row[i]) / 1000, 4))
                
                # Convert Annual_Average (index 24)
                if len(new_row) > 24 and new_row[24]:
                    new_row[24] = str(round(float(new_row[24]) / 1000, 4))
                
                # Also handle "Promedio_Anual" (index 20) which is like "3518,4"
                if len(new_row) > 20 and new_row[20]:
                    val = new_row[20].replace('"', '').replace(',', '.')
                    new_row[20] = str(round(float(val) / 1000, 4)).replace('.', ',')
                    
            except ValueError:
                pass
                
            writer.writerow(new_row)

print(f"Successfully converted {input_file} to kWh/m2. Original backed up to {backup_file}.")
