import joblib
import pandas as pd
import os

class ModelProvider:
    def __init__(self, model_path='../ml/models/xgboost_model.pkl'):
        self.model = None
        self.model_path = model_path
        self._load_model()

    def _load_model(self):
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                print("Successfully loaded ML model.")
            else:
                print(f"Warning: Model file not found at {self.model_path}. Using mock predictor.")
                self.model = None
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None

    def _preprocess(self, data: dict) -> pd.DataFrame:
        # This function should match the preprocessing steps from the ML notebook
        df = pd.DataFrame([data])
        
        # Example preprocessing: One-hot encode 'type'
        # In a real scenario, you'd use a saved encoder to ensure consistency
        df['type_CASH_IN'] = 1 if data.get('type') == 'CASH_IN' else 0
        df['type_CASH_OUT'] = 1 if data.get('type') == 'CASH_OUT' else 0
        df['type_DEBIT'] = 1 if data.get('type') == 'DEBIT' else 0
        df['type_PAYMENT'] = 1 if data.get('type') == 'PAYMENT' else 0
        df['type_TRANSFER'] = 1 if data.get('type') == 'TRANSFER' else 0
        
        # Feature selection to match model's expected input
        # This is a placeholder list
        expected_features = [
            'step', 'amount', 'oldbalanceOrg', 'newbalanceOrig', 
            'oldbalanceDest', 'newbalanceDest', 'type_CASH_IN', 
            'type_CASH_OUT', 'type_DEBIT', 'type_PAYMENT', 'type_TRANSFER'
        ]
        
        # Ensure all expected columns exist, fill missing with 0
        for col in expected_features:
            if col not in df.columns:
                df[col] = 0
        
        return df[expected_features]

    def predict(self, data: dict):
        if self.model is None:
            # Mock prediction logic
            import random
            is_suspicious = data.get('amount', 0) > 100000
            confidence = random.uniform(0.7, 0.99) if is_suspicious else random.uniform(0.1, 0.4)
            return {
                "is_suspicious": is_suspicious,
                "confidence_score": confidence
            }

        processed_df = self._preprocess(data)
        
        prediction_proba = self.model.predict_proba(processed_df)[:, 1]
        is_suspicious = prediction_proba[0] > 0.5 
        
        return {
            "is_suspicious": bool(is_suspicious),
            "confidence_score": float(prediction_proba[0])
        }

model_provider = ModelProvider()
