import pandas as pd
import argparse
import os

def preprocess_data(input_path, output_path):
    """
    Loads raw transaction data, filters it, performs one-hot encoding,
    and saves the processed data to a new CSV file.
    """
    print(f"Loading data from {input_path}...")
    try:
        df = pd.read_csv(input_path)
        print("Dataset loaded successfully.")
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_path}")
        return

    # --- Start of Preprocessing Logic ---

    # 1. Filter for relevant transaction types
    print("Filtering for 'CASH_OUT' and 'TRANSFER' types...")
    df_filtered = df[df['type'].isin(['CASH_OUT', 'TRANSFER'])].copy()
    
    if df_filtered.empty:
        print("Warning: No 'CASH_OUT' or 'TRANSFER' transactions found.")
        return

    # 2. One-hot encode the 'type' column
    print("Performing one-hot encoding on 'type' column...")
    df_processed = pd.get_dummies(df_filtered, columns=['type'], prefix='type', drop_first=True)

    # 3. Drop columns not needed for the model
    print("Dropping unnecessary columns...")
    columns_to_drop = ['isFlaggedFraud', 'nameOrig', 'nameDest']
    df_processed = df_processed.drop(columns=columns_to_drop)

    # --- End of Preprocessing Logic ---

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save the processed file
    df_processed.to_csv(output_path, index=False)
    print(f"Preprocessing complete. Processed file saved to {output_path}")
    print(f"Final shape of the processed data: {df_processed.shape}")


if __name__ == '__main__':
    # Set up argument parser to accept file paths from the command line
    parser = argparse.ArgumentParser(description="Preprocess transaction data for ML modeling.")
    
    parser.add_argument(
        '--input', 
        type=str, 
        required=True, 
        help="Path to the raw input CSV file (e.g., ../data/raw/paysim.csv)"
    )
    parser.add_argument(
        '--output', 
        type=str, 
        required=True, 
        help="Path to save the processed output CSV file (e.g., ../data/processed/processed_data.csv)"
    )
    
    args = parser.parse_args()
    
    # Run the preprocessing function with the provided arguments
    preprocess_data(args.input, args.output)

