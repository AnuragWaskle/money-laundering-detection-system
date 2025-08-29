import pandas as pd
import json
import fitz # PyMuPDF
import re

def process_uploaded_pdf(filepath: str):
    """
    Opens a PDF, extracts transaction data from its tables using PyMuPDF,
    and returns a pandas DataFrame with a standardized ("canonical") structure.
    """
    try:
        doc = fitz.open(filepath)
        transactions = []

        # Heuristics for identifying transaction columns
        # This can be expanded for more formats
        header_map = {
            'date': ['date', 'transaction date'],
            'description': ['description', 'details'],
            'debit': ['debit', 'withdrawal', 'payment'],
            'credit': ['credit', 'deposit']
        }

        for page_num, page in enumerate(doc):
            # find_tables() is a powerful feature in PyMuPDF
            tables = page.find_tables()
            if not tables:
                continue

            print(f"Found {len(tables)} tables on page {page_num + 1}.")

            for table in tables:
                # Extract data into a pandas DataFrame
                df = table.to_pandas()
                
                # --- Real-world data cleaning ---
                # Standardize column headers
                df.columns = [str(c).lower().strip() for c in df.columns]

                # Find which columns correspond to our needs
                # This is a simple version; a more advanced one could use fuzzy matching
                date_col = next((c for c in df.columns if any(h in c for h in header_map['date'])), None)
                desc_col = next((c for c in df.columns if any(h in c for h in header_map['description'])), None)
                debit_col = next((c for c in df.columns if any(h in c for h in header_map['debit'])), None)
                credit_col = next((c for c in df.columns if any(h in c for h in header_map['credit'])), None)

                # If we can't find the essential columns, skip this table
                if not all([date_col, desc_col, debit_col, credit_col]):
                    continue

                for index, row in df.iterrows():
                    # Clean and convert amount
                    debit_val = pd.to_numeric(str(row[debit_col]).replace('$', '').replace(',', ''), errors='coerce') or 0
                    credit_val = pd.to_numeric(str(row[credit_col]).replace('$', '').replace(',', ''), errors='coerce') or 0
                    
                    amount = debit_val if debit_val > 0 else credit_val
                    trans_type = 'CASH_OUT' if debit_val > 0 else 'CASH_IN'

                    if amount == 0:
                        continue

                    # Simulate other fields since they are not in typical bank statements
                    transactions.append({
                        'step': index + 1, # Placeholder
                        'type': trans_type,
                        'amount': amount,
                        'nameOrig': 'PDF_Account', # Placeholder
                        'oldbalanceOrg': 0, # Placeholder
                        'newbalanceOrig': 0, # Placeholder
                        'nameDest': str(row[desc_col]), # Use description as destination
                        'oldbalanceDest': 0, # Placeholder
                        'newbalanceDest': 0, # Placeholder
                        'isFraud': 0, # Assume not fraud by default from PDF
                        'isFlaggedFraud': 0
                    })

        doc.close()

        if not transactions:
            print("Warning: Could not extract any valid transactions from the PDF.")
            return None

        final_df = pd.DataFrame(transactions)
        print(f"Successfully processed {filepath} and extracted {len(final_df)} transactions.")
        return final_df

    except Exception as e:
        print(f"An error occurred during PDF processing: {e}")
        return None


def process_uploaded_csv(filepath: str, mapping_json: str):
    """
    Reads a CSV file, renames columns based on a user-provided mapping,
    validates required columns, and returns a pandas DataFrame.
    """
    try:
        df = pd.read_csv(filepath)
        mapping = json.loads(mapping_json)
        rename_map = {v: k for k, v in mapping.items() if v}
        df.rename(columns=rename_map, inplace=True)
        
        canonical_columns = [
            'step', 'type', 'amount', 'nameOrig', 'oldbalanceOrg', 
            'newbalanceOrig', 'nameDest', 'oldbalanceDest', 
            'newbalanceDest', 'isFraud'
        ]
        
        missing_cols = [col for col in canonical_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Mapping is incomplete. Required fields not mapped: {missing_cols}")
        
        if 'isFlaggedFraud' not in df.columns:
            df['isFlaggedFraud'] = 0

        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        df.dropna(subset=['amount'], inplace=True)
        
        print(f"Successfully processed {filepath} using user-provided mapping.")
        return df[canonical_columns + ['isFlaggedFraud']]

    except Exception as e:
        print(f"An error occurred during CSV processing: {e}")
        return None
