import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

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
    annual_precipitation = annual_precipitation[(annual_precipitation['year'] >= 2000) & (annual_precipitation['year'] <= 2100)]
    driest_year = annual_precipitation.loc[annual_precipitation['total_precipitation'].idxmin()]
    wettest_year = annual_precipitation.loc[annual_precipitation['total_precipitation'].idxmax()]
    return driest_year, wettest_year

def generate_plots(annual_precipitation, output_folder):
    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 5))
    
    # Gràfic de precipitació anual
    sns.lineplot(x='year', y='total_precipitation', data=annual_precipitation, marker='o')
    plt.title('Precipitació Anual')
    plt.xlabel('Any')
    plt.ylabel('Precipitació Total (mm)')
    plt.savefig(os.path.join(output_folder, 'precipitation_trend.png'))
    plt.show()

def process_folder(folder_path, output_folder):
    all_data = pd.DataFrame()
    
    os.makedirs(output_folder, exist_ok=True)

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.dat'):
                file_path = os.path.join(root, file)
                try:
                    df = read_dat_file(file_path)
                    annual_precipitation = calculate_annual_precipitation(df)
                    calculate_annual_variation_rate(annual_precipitation)
                    all_data = pd.concat([all_data, annual_precipitation])
                except Exception as e:
                    print(f"Error procesando {file}: {e}")
    
    all_data_grouped = all_data.groupby('year').agg({'total_precipitation': 'sum', 'median_precipitation': 'median'}).reset_index()
    all_data_grouped = all_data_grouped[(all_data_grouped['year'] >= 2000) & (all_data_grouped['year'] <= 2100)]
    driest_year, wettest_year = find_extreme_years(all_data_grouped)
    
    print("Resumen Estadístico:")
    print(all_data_grouped.describe())
    
    generate_plots(all_data_grouped, output_folder)
    
    all_data_grouped.to_csv(os.path.join(output_folder, 'annual_precipitation.csv'), index=False)
    
    print(f"Datos exportados en {output_folder}")

# Ús
dataset_folder = '/workspaces/ta06-Alex-Jimenez-Grup3/Todo/'
output_folder = os.path.join(os.path.dirname(__file__), 'output')
process_folder(dataset_folder, output_folder)