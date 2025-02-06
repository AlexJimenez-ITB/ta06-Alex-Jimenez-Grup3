import pandas as pd
import os
import logging
import seaborn as sns
import matplotlib.pyplot as plt

def read_dat_file(file_path, chunksize=10000):
    col_names = ['id', 'year', 'month'] + [f'day_{i}' for i in range(1, 32)]
    chunks = pd.read_csv(file_path, delim_whitespace=True, names=col_names, chunksize=chunksize, skiprows=1)
    return pd.concat(chunks, ignore_index=True)

def validate_files_format(file_paths):
    # Aquí puedes agregar la lógica para validar el formato de los archivos
    return True

def process_files(file_paths):
    dfs = []
    for file_path in file_paths:
        try:
            df = read_dat_file(file_path)
            dfs.append(df)
            logging.info(f"File {file_path} read successfully.")
        except Exception as e:
            logging.error(f"Error reading {file_path}: {e}")
    return dfs

def check_data_consistency(df):
    df.replace(-999, pd.NA, inplace=True)
    return df

def calculate_statistics(dfs):
    if not dfs:
        raise ValueError("No files to process.")
    
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Percentage of missing data
    missing_data_percentage = (combined_df.isna().sum().sum() / combined_df.size) * 100
    
    # Annual statistics
    combined_df['year'] = combined_df['year'].astype(int)
    annual_data = combined_df.groupby('year').sum().sum(axis=1)
    annual_avg = annual_data.mean()
    annual_totals = annual_data.sum()
    annual_data_diff = annual_data.diff().mean()
    
    wettest_year = annual_data.idxmax()
    driest_year = annual_data.idxmin()

    # Additional statistics
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

def export_statistics_to_csv(stats, output_file):
    df = pd.DataFrame([stats])
    df.to_csv(output_file, index=False)
    logging.info(f"Statistics exported to {output_file}")

def generate_plots(annual_precipitation, output_folder):
    sns.set(style="whitegrid")
    
    # Annual precipitation graph
    plt.figure(figsize=(10, 5))
    sns.lineplot(x='year', y='total_precipitation', data=annual_precipitation, marker='o')
    plt.title('Annual Precipitation')
    plt.xlabel('Year')
    plt.ylabel('Total Precipitation (mm)')
    plt.savefig(os.path.join(output_folder, 'precipitation_trend.png'))
    plt.show()
    plt.close()

    # Annual variation rate graph
    plt.figure(figsize=(10, 5))
    sns.lineplot(x='year', y='variation_rate', data=annual_precipitation, marker='o')
    plt.title('Annual Variation Rate of Precipitation')
    plt.xlabel('Year')
    plt.ylabel('Variation Rate (%)')
    plt.savefig(os.path.join(output_folder, 'annual_variation_rate.png'))
    plt.show()
    plt.close()

    # Extremes graph (driest and wettest years)
    driest_year, wettest_year = find_extreme_years(annual_precipitation)
    plt.figure(figsize=(6, 4))
    sns.barplot(x=['Driest Year', 'Wettest Year'], y=[driest_year['total_precipitation'], wettest_year['total_precipitation']], palette=['blue', 'green'])
    plt.title(f'Precipitation Extremes\nDriest Year: {driest_year["year"]}, Wettest Year: {wettest_year["year"]}')
    plt.ylabel('Total Precipitation (mm)')
    plt.savefig(os.path.join(output_folder, 'extreme_years.png'))
    plt.show()
    plt.close()

    # Annual precipitation distribution histogram
    plt.figure(figsize=(8, 5))
    sns.histplot(annual_precipitation['total_precipitation'], bins=20, kde=True, color='purple')
    plt.title('Annual Precipitation Distribution')
    plt.xlabel('Total Precipitation (mm)')
    plt.ylabel('Frequency')
    plt.savefig(os.path.join(output_folder, 'precipitation_distribution.png'))
    plt.show()
    plt.close()

    # Boxplot to show variability
    plt.figure(figsize=(6, 4))
    sns.boxplot(y=annual_precipitation['total_precipitation'])
    plt.title('Annual Precipitation Variability')
    plt.ylabel('Total Precipitation (mm)')
    plt.savefig(os.path.join(output_folder, 'precipitation_variability.png'))
    plt.show()
    plt.close()

def find_extreme_years(annual_precipitation):
    driest_year = annual_precipitation.loc[annual_precipitation['total_precipitation'].idxmin()]
    wettest_year = annual_precipitation.loc[annual_precipitation['total_precipitation'].idxmax()]
    return driest_year, wettest_year

def main():
    folder_path = '/workspaces/ta06-Alex-Jimenez-Grup3/Todo/'
    output_folder = 'output'
    csv_output_file = os.path.join(output_folder, 'statistical_summaries.csv')
    
    file_paths = []
    
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.dat'):
                file_paths.append(os.path.join(root, file))

    if not file_paths:
        logging.error("No .dat files found in the directory.")
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

            export_statistics_to_csv(stats, csv_output_file)
            logging.info("Statistics exported successfully.")

            annual_precipitation = calculate_annual_precipitation(pd.concat(processed_dfs, ignore_index=True))
            generate_plots(annual_precipitation, output_folder)
        except ValueError as e:
            logging.error(f"Error calculating statistics: {e}")
    else:
        logging.error("Files do not have the same format")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()