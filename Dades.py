import pandas as pd
import os

def validate_files(directory):
    if not os.path.exists(directory):
        print(f"Error: El directori {directory} no existeix.")
        return

    files = [f for f in os.listdir(directory) if f.endswith('.csv')]
    if not files:
        print("No s'han trobat fitxers CSV al directori.")
        return

    formats = []

    for file in files:
        file_path = os.path.join(directory, file)
        try:
            df = pd.read_csv(file_path, nrows=5)
            formats.append({
                'file': file,
                'columns': df.columns.tolist(),
                'delimiter': detect_delimiter(file_path)
            })
            print(f"Fitxer {file} llegit correctament.")
        except Exception as e:
            print(f"Error llegint {file}: {e}")

    # Check if all files have the same format
    reference_format = formats[0]
    for fmt in formats[1:]:
        if fmt['columns'] != reference_format['columns'] or fmt['delimiter'] != reference_format['delimiter']:
            print(f"El fitxer {fmt['file']} té un format diferent.")
        else:
            print(f"El format del fitxer {fmt['file']} és consistent.")

def detect_delimiter(file_path):
    with open(file_path, 'r') as file:
        line = file.readline()
        if ',' in line:
            return ','
        elif '\t' in line:
            return '\t'
        elif ' ' in line:
            return ' '
        else:
            return None

# Exemple d'ús
directory = '/workspaces/ta06-Alex-Jimenez-Grup3/'
validate_files(directory)