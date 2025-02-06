import pandas as pd
import os
import logging

# Configuració del logging
logging.basicConfig(filename='process_log.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

def read_dat_file(file_path, chunksize=10000):
    col_names = ['id', 'year', 'month'] + [f'day_{i}' for i in range(1, 32)]
    chunks = pd.read_csv(file_path, delim_whitespace=True, names=col_names, chunksize=chunksize, skiprows=1)
    return pd.concat(chunks, ignore_index=True)

def read_file(file_path):
    try:
        # Llegir el fitxer .dat
        df = read_dat_file(file_path)
        logging.info(f"Fitxer {file_path} llegit correctament.")
        return df
    except Exception as e:
        logging.error(f"Error llegint {file_path}: {e}")
        return None

def validate_file_format(file_path):
    df = read_file(file_path)
    if df is not None:
        # Validar el nombre de columnes i tipus de dades
        expected_columns = ['id', 'year', 'month'] + [f'day_{i}' for i in range(1, 32)]
        if list(df.columns) == expected_columns:
            logging.info(f"El format del fitxer {file_path} és correcte.")
            return True
        else:
            logging.warning(f"El format del fitxer {file_path} no és correcte.")
            return False
    return False

def process_data(df):
    # Reemplaçar valors mancants
    df.replace(-999, pd.NA, inplace=True)
    # Fondre les columnes de dies en files
    df_melted = df.melt(id_vars=['id', 'year', 'month'], value_vars=[f'day_{i}' for i in range(1, 32)],
                        var_name='day', value_name='precipitation')
    df_melted.dropna(subset=['precipitation'], inplace=True)
    df_melted['precipitation'] = pd.to_numeric(df_melted['precipitation'], errors='coerce')
    df_melted.dropna(subset=['precipitation'], inplace=True)
    return df_melted

def calculate_statistics(df):
    annual_precipitation = df.groupby('year')['precipitation'].agg(['sum', 'mean', 'median']).reset_index()
    annual_precipitation.columns = ['year', 'total_precipitation', 'mean_precipitation', 'median_precipitation']
    return annual_precipitation

def process_subfolder(subfolder_path):
    all_data = pd.DataFrame()
    for root, _, files in os.walk(subfolder_path):
        for file in files:
            if file.endswith('.dat'):
                file_path = os.path.join(root, file)
                logging.info(f"Processant fitxer: {file_path}")
                if validate_file_format(file_path):
                    df = read_file(file_path)
                    if df is not None:
                        processed_data = process_data(df)
                        all_data = pd.concat([all_data, processed_data])
                        logging.info(f"Dades del fitxer {file_path} processades correctament.")
    
    if not all_data.empty:
        annual_precipitation = calculate_statistics(all_data)
        output_file = os.path.join(subfolder_path, 'annual_precipitation_summary.csv')
        annual_precipitation.to_csv(output_file, index=False)
        logging.info(f"Dades processades i exportades correctament a {output_file}.")
    else:
        logging.warning(f"No s'han processat dades a {subfolder_path}.")

def main(folder_path):
    for subfolder in os.listdir(folder_path):
        subfolder_path = os.path.join(folder_path, subfolder)
        if os.path.isdir(subfolder_path):
            logging.info(f"Processant subcarpeta: {subfolder_path}")
            process_subfolder(subfolder_path)

if __name__ == "__main__":
    folder_path = '/workspaces/ta06-Alex-Jimenez-Grup3/Todo'
    main(folder_path)