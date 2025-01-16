import pandas as pd
import os

def validate_files(directory):
    if not os.path.exists(directory):
        print(f"Error: El directori {directory} no existeix.")
        return

    files = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith('.dat'):
                files.append(os.path.join(root, filename))

    if not files:
        print("No s'han trobat fitxers .dat al directori.")
        return

    formats = []

    for file_path in files:
        try:
            df = read_dat_file(file_path, nrows=5)
            formats.append({
                'file': file_path,
                'columns': df.columns.tolist()
            })
            print(f"Fitxer {file_path} llegit correctament.")
        except Exception as e:
            print(f"Error llegint {file_path}: {e}")

    # Check if all files have the same format
    reference_format = formats[0]
    for fmt in formats[1:]:
        if fmt['columns'] != reference_format['columns']:
            print(f"El fitxer {fmt['file']} té un format diferent.")
        else:
            print(f"El format del fitxer {fmt['file']} és consistent.")

def read_dat_file(file_path, nrows=None):
    # Llegir el fitxer .dat amb pandas
    col_names = ['id', 'year', 'month'] + [f'day_{i}' for i in range(1, 32)]
    df = pd.read_csv(file_path, delim_whitespace=True, header=None, names=col_names, nrows=nrows)
    return df

def calculate_statistics(file_path):
    df = read_dat_file(file_path)
    
    # Reemplaçar valors mancants (-999) amb NaN
    df.replace(-999, pd.NA, inplace=True)
    
    # Percentatge de dades mancants
    missing_percentage = df.isna().mean() * 100
    print("Percentatge de dades mancants per columna:")
    print(missing_percentage)
    
    # Estadístiques bàsiques
    print("Estadístiques bàsiques:")
    print(df.describe())
    
    # Convertir les dades a un format llarg per facilitar l'anàlisi
    df_long = df.melt(id_vars=['id', 'year', 'month'], var_name='day', value_name='precipitation')
    df_long['day'] = df_long['day'].str.extract('(\d+)').astype(int)
    df_long['date'] = pd.to_datetime(df_long[['year', 'month', 'day']])
    
    # Mitjanes i totals anuals
    annual_precipitation = df_long.groupby(df_long['date'].dt.year)['precipitation'].agg(['sum', 'mean'])
    print("Precipitació total i mitjana per any:")
    print(annual_precipitation)
    
    # Tendència de canvi
    annual_precipitation['change_rate'] = annual_precipitation['sum'].pct_change() * 100
    print("Taxa de variació anual de les precipitacions:")
    print(annual_precipitation['change_rate'])
    
    # Extrems
    most_rainy_year = annual_precipitation['sum'].idxmax()
    least_rainy_year = annual_precipitation['sum'].idxmin()
    print(f"Any més plujós: {most_rainy_year}")
    print(f"Any més sec: {least_rainy_year}")
    
    # Estadístiques addicionals
    annual_std = df_long.groupby(df_long['date'].dt.year)['precipitation'].std()
    annual_median = df_long.groupby(df_long['date'].dt.year)['precipitation'].median()
    print("Desviació estàndard anual de les precipitacions:")
    print(annual_std)
    print("Mediana anual de les precipitacions:")
    print(annual_median)

# Exemple d'ús
directory = '/workspaces/ta06-Alex-Jimenez-Grup3/Todo/'
validate_files(directory)

# Calcular estadístiques per a cada fitxer .dat
for root, _, filenames in os.walk(directory):
    for filename in filenames:
        if filename.endswith('.dat'):
            file_path = os.path.join(root, filename)
            print(f"Calculant estadístiques per al fitxer {file_path}:")
            calculate_statistics(file_path)