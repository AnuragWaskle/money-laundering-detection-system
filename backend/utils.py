import pandas as pd

def process_uploaded_csv(filepath: str):
    """
    Reads a CSV file from a given path, validates required columns,
    and returns a pandas DataFrame.
    """
    try:
        df = pd.read_csv(filepath)
        
        required_columns = [
            'step', 'type', 'amount', 'nameOrig', 'oldbalanceOrg', 
            'newbalanceOrig', 'nameDest', 'oldbalanceDest', 
            'newbalanceDest', 'isFraud', 'isFlaggedFraud'
        ]
        
        # Check if all required columns are present
        if not all(col in df.columns for col in required_columns):
            missing_cols = [col for col in required_columns if col not in df.columns]
            raise ValueError(f"CSV is missing required columns: {missing_cols}")
            
        # Basic data type conversions and cleaning
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        df.dropna(subset=['amount'], inplace=True)
        
        print(f"Successfully processed {filepath}, found {len(df)} rows.")
        return df

    except FileNotFoundError:
        print(f"Error: The file at {filepath} was not found.")
        return None
    except Exception as e:
        print(f"An error occurred during CSV processing: {e}")
        return None

