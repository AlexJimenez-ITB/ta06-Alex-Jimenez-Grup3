import pandas as pd
import os

def validate_files(directory):
    files = [f for f in os.listdir(directory) if f.endswith('.csv')]
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
        except Exception as e:
            print(f"Error reading {file}: {e}")

    # Check if all files have the same format
    reference_format = formats[0]
    for fmt in formats[1:]:
        if fmt['columns'] != reference_format['columns'] or fmt['delimiter'] != reference_format['delimiter']:
            print(f"File {fmt['file']} has a different format.")
        else:
            print(f"File {fmt['file']} format is consistent.")

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

def clean_data(file_path):
    try:
        df = pd.read_csv(file_path)
        # Example: Ensure numeric columns are indeed numeric
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        # Handle missing values
        df.fillna(method='ffill', inplace=True)
        return df
    except Exception as e:
        print(f"Error cleaning {file_path}: {e}")
        return None

# Example usage
directory = '/path/to/csv/files'
validate_files(directory)
for file in os.listdir(directory):
    if file.endswith('.csv'):
        file_path = os.path.join(directory, file)
        clean_data(file_path)