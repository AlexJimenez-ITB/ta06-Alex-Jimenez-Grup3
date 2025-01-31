import pandas as pd
import os
import logging

def read_dat_file(file_path, chunksize=10000):
    col_names = ['id', 'year', 'month'] + [f'day_{i}' for i in range(1, 32)]
    chunks = pd.read_csv(file_path, delim_whitespace=True, names=col_names, chunksize=chunksize, skiprows=1)
    return pd.concat(chunks, ignore_index=True)

def validate_files_format(file_paths):
    # Aquí pots afegir la lògica per validar el format dels fitxers
    return True

def process_files(file_paths):
    dfs = []
    for file_path in file_paths:
        try:
            df = read_dat_file(file_path)
            dfs.append(df)
            logging.info(f"File {file_path} read successfully.")
        except Exception as e:
            logging.error(f"Error llegint {file_path}: {e}")
    return dfs

def check_data_consistency(df):
    df.replace(-999, pd.NA, inplace=True)
    return df

def calculate_statistics(dfs):
    if not dfs:
        raise ValueError("No hi ha fitxers per processar.")
    
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Percentatge de dades mancants
    missing_data_percentage = (combined_df.isna().sum().sum() / combined_df.size) * 100
    
    # Estadístiques anuals
    combined_df['year'] = combined_df['year'].astype(int)
    annual_data = combined_df.groupby('year').sum().sum(axis=1)
    annual_avg = annual_data.mean()
    annual_totals = annual_data.sum()
    annual_data_diff = annual_data.diff().mean()
    
    wettest_year = annual_data.idxmax()
    driest_year = annual_data.idxmin()

    # Estadístiques addicionals
    monthly_avg = combined_df.groupby('month').mean().mean(axis=1)
    highest_monthly_avg = monthly_avg.max()
    lowest_monthly_avg = monthly_avg.min()

    return {
        "missing_data_percentage": missing_data_percentage,
        "annual_avg": annual_avg,
        "annual_totals": annual_totals,
        "annual_data_diff": annual_data_diff,
        "wettest_year": wettest_year,
        "driest_year": driest_year,
        "highest_monthly_avg": highest_monthly_avg,
        "lowest_monthly_avg": lowest_monthly_avg
    }

def main():
    folder_path = '/workspaces/ta06-Alex-Jimenez-Grup3/Todo/'
    file_paths = []
    
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.dat'):
                file_paths.append(os.path.join(root, file))

    if not file_paths:
        logging.error("No s'han trobat fitxers .dat al directori.")
        return

    if validate_files_format(file_paths):
        logging.info("All files have the same format")
        dfs = process_files(file_paths)
        if not dfs:
            logging.error("No data frames were processed.")
            return

        processed_dfs = [check_data_consistency(df) for df in dfs]

        try:
            stats = calculate_statistics(processed_dfs)
            logging.info("Statistics calculated successfully.")
            for key, value in stats.items():
                print(f"{key}: {value}")
        except ValueError as e:
            logging.error(f"Error calculating statistics: {e}")
    else:
        logging.error("Files do not have the same format")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()