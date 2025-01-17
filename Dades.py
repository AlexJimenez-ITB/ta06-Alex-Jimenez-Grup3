import pandas as pd
import os

def read_dat_file(file_path, chunksize=10000):
    # Llegir el fitxer .dat amb pandas en trossos
    col_names = ['id', 'year', 'month'] + [f'day_{i}' for i in range(1, 32)]
    chunks = pd.read_csv(file_path, delim_whitespace=True, header=None, names=col_names, chunksize=chunksize)
    return pd.concat(chunks, ignore_index=True)

def calculate_total_missing_percentage(file_path):
    if not os.path.exists(file_path):
        print(f"Error: El fitxer {file_path} no existeix.")
        return

    try:
        df = read_dat_file(file_path)
        print(f"Fitxer {file_path} llegit correctament.")
    except Exception as e:
        print(f"Error llegint {file_path}: {e}")
        return

    # Comptar valors -999 abans de reemplaçar-los
    missing_counts = (df == -999).sum()
    total_counts = df.count()
    missing_percentage = (missing_counts / total_counts) * 100

    print("Percentatge de dades mancants per columna en el fitxer:")
    print(missing_percentage.to_string(float_format=lambda x: f'{x:.2f}%'))

# Exemple d'ús
file_path = '/workspaces/ta06-Alex-Jimenez-Grup3/Todo/Parte_1/precip.P10033.MIROC5.RCP60.2006-2100.REGRESION.dat'
calculate_total_missing_percentage(file_path)