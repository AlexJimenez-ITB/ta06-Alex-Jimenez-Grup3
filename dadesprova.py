import pandas as pd
import os

def read_dat_file(file_path, chunksize=10000):
    col_names = ['id', 'year', 'month'] + [f'day_{i}' for i in range(1, 32)]
    chunks = pd.read_csv(file_path, delim_whitespace=True, names=col_names, chunksize=chunksize, skiprows=1)
    return pd.concat(chunks, ignore_index=True)

def calculate_annual_precipitation(df):
    df.replace(-999, pd.NA, inplace=True)
    df_melted = df.melt(id_vars=['id', 'year', 'month'], value_vars=[f'day_{i}' for i in range(1, 32)],
                        var_name='day', value_name='precipitation')
    df_melted.dropna(subset=['precipitation'], inplace=True)
    df_melted['precipitation'] = pd.to_numeric(df_melted['precipitation'], errors='coerce')
    df_melted.dropna(subset=['precipitation'], inplace=True)
    annual_precipitation = df_melted.groupby('year')['precipitation'].agg(['sum', 'median']).reset_index()
    annual_precipitation.columns = ['year', 'total_precipitation', 'median_precipitation']
    return annual_precipitation

def calculate_annual_variation_rate(annual_precipitation):
    annual_precipitation['variation_rate'] = annual_precipitation['total_precipitation'].pct_change() * 100

def find_extreme_years(annual_precipitation):
    annual_precipitation = annual_precipitation[(annual_precipitation['year'] >= 2006) & (annual_precipitation['year'] <= 2100)]
    driest_year = annual_precipitation.loc[annual_precipitation['total_precipitation'].idxmin()]
    wettest_year = annual_precipitation.loc[annual_precipitation['total_precipitation'].idxmax()]
    return driest_year, wettest_year

def calculate_total_missing_percentage(file_path):
    if not os.path.exists(file_path):
        print(f"Error: El fitxer {file_path} no existeix.")
        return None, None, None, None

    try:
        df = read_dat_file(file_path)
        print(f"Fitxer {file_path} llegit correctament.")
    except Exception as e:
        print(f"Error llegint {file_path}: {e}")
        return None, None, None, None

    missing_counts = (df == -999).sum().sum()
    total_counts = df.size
    missing_percentage = (missing_counts / total_counts) * 100

    annual_precipitation = calculate_annual_precipitation(df)
    calculate_annual_variation_rate(annual_precipitation)
    driest_year, wettest_year = find_extreme_years(annual_precipitation)

    return missing_percentage, annual_precipitation, driest_year, wettest_year

def process_folder(folder_path):
    all_data = pd.DataFrame()
    total_missing_counts = 0
    total_counts = 0

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.dat'):
                file_path = os.path.join(root, file)
                missing_percentage, annual_precipitation, driest_year, wettest_year = calculate_total_missing_percentage(file_path)
                if missing_percentage is not None:
                    all_data = pd.concat([all_data, annual_precipitation])
                    total_missing_counts += (missing_percentage / 100) * annual_precipitation.size
                    total_counts += annual_precipitation.size

    overall_missing_percentage = (total_missing_counts / total_counts) * 100
    all_data_grouped = all_data.groupby('year').agg({'total_precipitation': 'sum', 'median_precipitation': 'median'}).reset_index()
    driest_year, wettest_year = find_extreme_years(all_data_grouped)

    print("Informe general:")
    print("Percentatge de dades mancants (promig):")
    print(f'{overall_missing_percentage:.2f}%')

    print("\nPrecipitació anual agregada:")
    print(all_data_grouped)

    print("\nAny més sec i més plujós:")
    print(f"L'any més sec és {int(driest_year['year'])} amb {driest_year['total_precipitation']} mm de precipitació.")
    print(f"L'any més plujós és {int(wettest_year['year'])} amb {wettest_year['total_precipitation']} mm de precipitació.")

# Exemple d'ús
folder_path = '/workspaces/ta06-Alex-Jimenez-Grup3/Todo/Parte_1'
process_folder(folder_path)