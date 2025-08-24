import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import werkzeug.utils
import pandas as pd

# Import our custom modules
from ml_models import model_provider
from graph_db import db_provider
from utils import process_uploaded_csv

app = Flask(__name__)
CORS(app) 

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- One-time setup: Ensure DB constraints are set ---
with app.app_context():
    db_provider.setup_constraints()
# ----------------------------------------------------

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Backend is running."})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected for uploading"}), 400

    if file and file.filename.endswith('.csv'):
        try:
            filename = werkzeug.utils.secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # --- Real logic is now implemented ---
            # 1. Process the CSV file
            df = process_uploaded_csv(filepath)
            if df is None:
                return jsonify({"error": "Failed to process the uploaded CSV file."}), 400
            
            # 2. Add the transactions to our persistent graph
            db_provider.add_transactions_from_df(df)
            # ---------------------------------------

            return jsonify({
                "message": f"File '{filename}' successfully processed and {len(df)} transactions merged into the graph.",
                "filename": filename,
                "transactions_added": len(df)
            }), 200
        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    else:
        return jsonify({"error": "Invalid file type. Please upload a CSV file."}), 400

@app.route('/api/predict', methods=['POST'])
def handle_prediction():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400
    
    try:
        prediction_result = model_provider.predict(data)
        
        # Add a human-readable reason for the prediction
        prediction_result["transaction_id"] = data.get("id", "N/A")
        if prediction_result["is_suspicious"]:
            prediction_result["reason"] = f"Flagged with {prediction_result['confidence_score']:.0%} confidence."
        else:
            prediction_result["reason"] = "Considered normal activity."

        return jsonify(prediction_result), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred during prediction: {str(e)}"}), 500

@app.route('/api/graph-data', methods=['GET'])
def get_graph():
    account_id = request.args.get('account_id')
    if not account_id:
        return jsonify({"error": "account_id parameter is required"}), 400
        
    try:
        graph_data = db_provider.get_transaction_graph(account_id)
        if not graph_data["nodes"]:
             return jsonify({"message": f"No transactions found for account '{account_id}'." , "nodes": [], "links": []}), 404
        return jsonify(graph_data), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred fetching graph data: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
