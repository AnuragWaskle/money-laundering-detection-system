import joblib
import pandas as pd
import numpy as np
import os
import shap
import torch
from torch_geometric.data import Data
from torch_geometric.nn import SAGEConv
from transformers import pipeline

# --- GNN Model Definition (must match the training notebook) ---
class GNN(torch.nn.Module):
    def __init__(self, num_node_features, num_edge_features, hidden_channels):
        super(GNN, self).__init__()
        self.conv1 = SAGEConv(num_node_features, hidden_channels)
        self.conv2 = SAGEConv(hidden_channels, hidden_channels)
        self.output_layer = torch.nn.Linear(2 * hidden_channels + num_edge_features, 1)

    def forward(self, x, edge_index, edge_attr):
        x = self.conv1(x, edge_index).relu()
        x = self.conv2(x, edge_index)
        source_embed = x[edge_index[0]]
        dest_embed = x[edge_index[1]]
        combined = torch.cat([source_embed, dest_embed, edge_attr], dim=1)
        return torch.sigmoid(combined).squeeze()

class ModelProvider:
    def __init__(self):
        # XGBoost and SHAP artifacts
        self.xgb_model = None
        self.explainer = None
        self.xgb_columns = []
        # GNN artifacts
        self.gnn_model = None
        self.gnn_account_map = {}
        # Hugging Face Summarizer
        self.summarizer = None
        self._load_artifacts()

    def _load_artifacts(self):
        # Load XGBoost, SHAP, and columns
        try:
            self.xgb_model = joblib.load('../ml/models/xgboost_model.pkl')
            self.explainer = joblib.load('../ml/models/shap_explainer.pkl')
            self.xgb_columns = joblib.load('../ml/models/model_columns.pkl')
            print("Successfully loaded XGBoost and SHAP artifacts.")
        except Exception as e:
            print(f"Warning: Could not load XGBoost/SHAP artifacts: {e}")

        # Load GNN model and account map
        try:
            self.gnn_account_map = joblib.load('../ml/models/gnn_account_map.pkl')
            self.gnn_model = GNN(num_node_features=1, num_edge_features=5, hidden_channels=64)
            self.gnn_model.load_state_dict(torch.load('../ml/models/gnn_model.pt'))
            self.gnn_model.eval()
            print("Successfully loaded GNN artifacts.")
        except Exception as e:
            print(f"Warning: Could not load GNN artifacts: {e}")

        # Load Summarization Model
        try:
            print("Loading summarization model from Hugging Face...")
            # Using a smaller, faster model perfect for this task
            self.summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-6-6")
            print("Summarization model loaded successfully.")
        except Exception as e:
            print(f"Warning: Could not load summarization model: {e}")

    def _preprocess(self, data: dict) -> pd.DataFrame:
        df = pd.DataFrame([data])
        df['type_TRANSFER'] = 1 if data.get('type') == 'TRANSFER' else 0
        for col in self.xgb_columns:
            if col not in df.columns:
                df[col] = 0
        return df[self.xgb_columns]

    def _get_explanation(self, shap_values, features: pd.DataFrame) -> str:
        shap_df = pd.DataFrame({'feature': features.columns, 'shap_value': shap_values[0]}).sort_values(by='shap_value', key=abs, ascending=False).head(3)
        reasons = [f"'{row['feature']}' which {'increases' if row['shap_value'] > 0 else 'decreases'} risk" for _, row in shap_df.iterrows()]
        return "Flagged due to: " + ", ".join(reasons) + "."

    def predict(self, data: dict):
        if not all([self.xgb_model, self.explainer, self.xgb_columns]):
            return {"is_suspicious": False, "confidence_score": 0.0, "reason": "XGBoost model not loaded."}
        
        processed_df = self._preprocess(data)
        proba = self.xgb_model.predict_proba(processed_df)[:, 1][0]
        is_suspicious = proba > 0.5
        reason = "Considered normal activity."
        if is_suspicious:
            shap_values = self.explainer.shap_values(processed_df)
            reason = self._get_explanation(shap_values, processed_df)
        return {"is_suspicious": bool(is_suspicious), "confidence_score": float(proba), "reason": reason}

    def predict_with_gnn(self, graph_data: dict):
        if not self.gnn_model:
            return {"error": "GNN model not loaded."}
        
        # Convert the graph data from Neo4j into a PyG Data object
        nodes = graph_data['nodes']
        links = graph_data['links']
        
        # Create a local map for the subgraph
        local_node_map = {node['id']: i for i, node in enumerate(nodes)}
        
        if not local_node_map:
            return {"predictions": []}

        # Create edge index
        source_nodes = [local_node_map[link['source']] for link in links]
        dest_nodes = [local_node_map[link['target']] for link in links]
        edge_index = torch.tensor([source_nodes, dest_nodes], dtype=torch.long)

        # Create node and edge features (simplified for inference)
        x = torch.ones((len(nodes), 1), dtype=torch.float) # Placeholder node features
        edge_attr = torch.tensor([link.get('amount', 0) for link in links], dtype=torch.float).view(-1, 1)
        # Pad edge attributes if they don't match the model's expected input
        if edge_attr.shape[1] < 5:
            padding = torch.zeros(edge_attr.shape[0], 5 - edge_attr.shape[1])
            edge_attr = torch.cat([edge_attr, padding], dim=1)

        with torch.no_grad():
            predictions = self.gnn_model(x, edge_index, edge_attr)
        
        results = []
        for i, link in enumerate(links):
            results.append({
                "source": link['source'],
                "target": link['target'],
                "gnn_risk_score": float(predictions[i])
            })
        return {"predictions": results}

    def generate_summary(self, history_df: pd.DataFrame):
        if self.summarizer is None:
            return "Summarization model is not available."
        if history_df.empty:
            return "No transaction history available to summarize."

        # Convert transaction history to a text prompt
        prompt_text = "Transaction history: "
        for _, row in history_df.iterrows():
            if row['direction'] == 'outgoing':
                prompt_text += f"sent {int(row['amount'])} to {row['other_party']}; "
            else:
                prompt_text += f"received {int(row['amount'])} from {row['other_party']}; "
        
        # Generate summary
        summary = self.summarizer(prompt_text, max_length=60, min_length=15, do_sample=False)
        return summary[0]['summary_text']

model_provider = ModelProvider()