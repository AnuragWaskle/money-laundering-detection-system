import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import werkzeug.utils
import pandas as pd

# Assuming other modules will be created later
# from ml_models import predict_transaction
# from graph_db import get_graph_data, add_transactions_to_graph
# from utils import process_uploaded_file

app = Flask(__name__)
CORS(app) 

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
            
            # Placeholder for processing and adding to graph
            # df = process_uploaded_file(filepath)
            # add_transactions_to_graph(df)

            return jsonify({
                "message": "File successfully uploaded and processing started.",
                "filename": filename
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
        # Placeholder for prediction logic
        # prediction_result = predict_transaction(data)
        
        # Mock response for now
        import random
        is_suspicious = random.choice([True, False])
        confidence = random.uniform(0.5, 0.99)
        
        prediction_result = {
            "transaction_id": data.get("id", "N/A"),
            "is_suspicious": is_suspicious,
            "confidence_score": f"{confidence:.2f}",
            "reason": "High transaction frequency" if is_suspicious else "Normal activity"
        }
        
        return jsonify(prediction_result), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred during prediction: {str(e)}"}), 500

@app.route('/api/graph-data', methods=['GET'])
def get_graph():
    account_id = request.args.get('account_id')
    if not account_id:
        return jsonify({"error": "account_id parameter is required"}), 400
        
    try:
        # Placeholder for graph data fetching
        # graph_data = get_graph_data(account_id)

        # Mock response for now
        nodes = [
            {"id": "acc_1", "label": "Account 1"},
            {"id": "acc_2", "label": "Account 2"},
            {"id": "acc_3", "label": "Account 3"},
            {"id": "acc_4", "label": "Account 4"},
        ]
        links = [
            {"source": "acc_1", "target": "acc_2", "label": "$5000"},
            {"source": "acc_2", "target": "acc_3", "label": "$4800"},
            {"source": "acc_3", "target": "acc_1", "label": "$4750"},
            {"source": "acc_2", "target": "acc_4", "label": "$200"},
        ]
        graph_data = {"nodes": nodes, "links": links}
        
        return jsonify(graph_data), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred fetching graph data: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
