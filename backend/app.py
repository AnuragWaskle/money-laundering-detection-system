import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import werkzeug.utils
import pandas as pd

from ml_models import model_provider
from graph_db import db_provider
from utils import process_uploaded_csv, process_uploaded_pdf

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'Uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

with app.app_context():
    db_provider.setup_constraints()

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Backend is running."}), 200

@app.route('/api/transaction', methods=['POST'])
def handle_realtime_transaction():
    transaction_data = request.get_json()

    required_fields = ['step', 'type', 'amount', 'nameOrig', 'nameDest']
    if not transaction_data or not all(field in transaction_data for field in required_fields):
        return jsonify({"error": "Invalid or incomplete transaction data"}), 400
    try:
        prediction = model_provider.predict(transaction_data)
        df = pd.DataFrame([transaction_data])
        db_provider.add_transactions_from_df(df)
        response = { "message": "Transaction processed", **prediction }

    # Validate the incoming data
    required_fields = ['step', 'type', 'amount', 'nameOrig', 'nameDest']
    if not transaction_data or not all(field in transaction_data for field in required_fields):
        return jsonify({"error": "Invalid or incomplete transaction data"}), 400

    try:
        # Get a real-time prediction from the ML model
        prediction = model_provider.predict(transaction_data)

        # Add the transaction to the persistent knowledge graph
        df = pd.DataFrame([transaction_data])
        db_provider.add_transactions_from_df(df)

        # Return the result
        response = {
            "message": "Transaction processed and added to graph.",
            "transaction_id": transaction_data.get('step', 'N/A'),
            "is_suspicious": prediction.get('is_suspicious'),
            "confidence_score": prediction.get('confidence_score')
        }

        return jsonify(response), 201
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/api/upload-csv', methods=['POST'])
def upload_csv():
    if 'file' not in request.files or 'mapping' not in request.form:
        return jsonify({"error": "File or mapping data is missing"}), 400

    file = request.files['file']
    mapping_json = request.form['mapping']
    if file.filename == '' or not file.filename.endswith('.csv'):
        return jsonify({"error": "Invalid or missing CSV file"}), 400

    file = request.files['file']
    mapping_json = request.form['mapping']
    
    if file.filename == '' or not file.filename.endswith('.csv'):
        return jsonify({"error": "Invalid or missing CSV file"}), 400

    try:
        filename = werkzeug.utils.secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        df = process_uploaded_csv(filepath, mapping_json)
        if df is None:
            return jsonify({"error": "Failed to process CSV with the provided mapping."}), 400
        db_provider.add_transactions_from_df(df)
        return jsonify({"message": f"CSV '{filename}' processed, {len(df)} transactions merged.","filename": filename,"transactions_added": len(df)}), 200

        df = process_uploaded_csv(filepath, mapping_json)
        if df is None:
            return jsonify({"error": "Failed to process CSV with the provided mapping."}), 400
        
        db_provider.add_transactions_from_df(df)
        return jsonify({
            "message": f"CSV '{filename}' processed, {len(df)} transactions merged.",
            "filename": filename,
            "transactions_added": len(df)
        }), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/api/upload-pdf', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '' or not file.filename.endswith('.pdf'):
        return jsonify({"error": "Invalid or missing PDF file"}), 400

    file = request.files['file']
    
    if file.filename == '' or not file.filename.endswith('.pdf'):
        return jsonify({"error": "Invalid or missing PDF file"}), 400

    try:
        filename = werkzeug.utils.secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        df = process_uploaded_pdf(filepath)
        if df is None:
            return jsonify({"error": "Failed to extract transactions from the PDF."}), 400
        db_provider.add_transactions_from_df(df)
        return jsonify({"message": f"PDF '{filename}' processed, {len(df)} transactions merged.","filename": filename,"transactions_added": len(df)}), 200

        df = process_uploaded_pdf(filepath)
        if df is None:
            return jsonify({"error": "Failed to extract transactions from the PDF."}), 400
        
        db_provider.add_transactions_from_df(df)
        return jsonify({
            "message": f"PDF '{filename}' processed, {len(df)} transactions merged.",
            "filename": filename,
            "transactions_added": len(df)
        }), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/api/predict', methods=['POST'])
def handle_prediction():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400
    try:
        prediction_result = model_provider.predict(data)
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
            return jsonify({"message": f"No transactions found for account '{account_id}'.", "nodes": [], "links": []}), 404
        return jsonify(graph_data), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred fetching graph data: {str(e)}"}), 500

@app.route('/api/analyze-graph/<string:account_id>', methods=['GET'])
def analyze_account_graph(account_id):
    try:

        graph_data = db_provider.get_transaction_graph(account_id, limit=100)
        if not graph_data or not graph_data['nodes']:
            return jsonify({"message": f"No graph data found for account {account_id}"}), 404
        gnn_results = model_provider.predict_with_gnn(graph_data)

        # Fetch the subgraph for the account from Neo4j
        graph_data = db_provider.get_transaction_graph(account_id, limit=100)
        if not graph_data or not graph_data['nodes']:
            return jsonify({"message": f"No graph data found for account {account_id}"}), 404
        
        # Get predictions for the subgraph using the GNN
        gnn_results = model_provider.predict_with_gnn(graph_data)
        

        return jsonify(gnn_results), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred during graph analysis: {str(e)}"}), 500

@app.route('/api/account-summary/<string:account_id>', methods=['GET'])
def get_account_summary(account_id):
    try:

        history_df = db_provider.get_account_history(account_id)
        if history_df is None or history_df.empty:
            return jsonify({"summary": "No transaction history found for this account."}), 404
        summary = model_provider.generate_summary(history_df)

        # Fetch transaction history from the graph database
        history_df = db_provider.get_account_history(account_id)
        if history_df is None or history_df.empty:
            return jsonify({"summary": "No transaction history found for this account."}), 404

        # Generate the summary using our model provider
        summary = model_provider.generate_summary(history_df)
        

        return jsonify({"account_id": account_id, "summary": summary}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred during summarization: {str(e)}"}), 500

# --- ANALYSIS ENDPOINTS ---
@app.route('/api/graph/find-cycles', methods=['GET'])
def find_cycles_endpoint():
    try:
        nodes_in_cycles = db_provider.find_all_cycles()
        return jsonify({"nodes": nodes_in_cycles}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred while finding cycles: {str(e)}"}), 500

@app.route('/api/graph/find-high-risk', methods=['GET'])
def find_high_risk_endpoint():
    try:
        high_risk_nodes = db_provider.find_high_risk_nodes()
        return jsonify({"nodes": high_risk_nodes}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred while finding high-risk nodes: {str(e)}"}), 500

# --- NEW: NAVIGATION PAGE ENDPOINTS ---
@app.route('/api/global-dashboard', methods=['GET'])
def get_global_dashboard():
    """Endpoint for Global Dashboard page"""
    try:
        # Get overall statistics
        total_accounts = db_provider.get_total_accounts()
        total_transactions = db_provider.get_total_transactions()
        high_risk_count = len(db_provider.find_high_risk_nodes())
        cycles_count = len(db_provider.find_all_cycles())
        
        stats = {
            "total_accounts": total_accounts,
            "total_transactions": total_transactions,
            "high_risk_accounts": high_risk_count,
            "suspicious_cycles": cycles_count
        }
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"error": f"Could not fetch global dashboard data: {str(e)}"}), 500

@app.route('/api/cases', methods=['GET'])
def get_cases():
    """Endpoint for Case Management page"""
    try:
        # Get all high-risk cases
        high_risk_nodes = db_provider.find_high_risk_nodes()
        cases = []
        for node in high_risk_nodes[:20]:  # Limit to top 20 cases
            try:
                account_id = node.get('account_id', 'Unknown')
                risk_score = node.get('risk_score', 0)
                cases.append({
                    "case_id": f"CASE-{account_id}",
                    "account_id": account_id,
                    "risk_score": risk_score,
                    "status": "Open" if risk_score > 0.7 else "Under Review",
                    "created_date": "2025-08-29"  # You might want to get this from your data
                })
            except:
                continue
        return jsonify({"cases": cases}), 200
    except Exception as e:
        return jsonify({"error": f"Could not fetch cases: {str(e)}"}), 500

@app.route('/api/trace-investigate', methods=['GET', 'POST'])
def trace_investigate():
    """Endpoint for Trace & Investigate page"""
    if request.method == 'GET':
        # Return available trace data or instructions
        return jsonify({
            "message": "Trace investigation ready",
            "available_accounts": db_provider.get_all_account_ids()[:50]  # Sample accounts
        }), 200
    
    elif request.method == 'POST':
        # Handle trace analysis request
        data = request.get_json()
        account_id = data.get('account_id')
        if not account_id:
            return jsonify({"error": "account_id is required"}), 400
        
        try:
            # Get transaction path for the account
            trace_data = db_provider.get_transaction_path(account_id)
            if not trace_data:
                return jsonify({"error": "No trace data found for this account"}), 404
            
            # If you have the LSTM model, you can add trace analysis here
            # For now, return basic trace information
            return jsonify({
                "account_id": account_id,
                "trace_length": len(trace_data),
                "trace_data": trace_data,
                "message": "Trace analysis complete"
            }), 200
        except Exception as e:
            return jsonify({"error": f"Could not perform trace investigation: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)@app.route('/api/transaction', methods=['POST'])
def handle_realtime_transaction():
    transaction_data = request.get_json()
    
    # Validate the incoming data
    required_fields = ['step', 'type', 'amount', 'nameOrig', 'nameDest']
    if not transaction_data or not all(field in transaction_data for field in required_fields):
        return jsonify({"error": "Invalid or incomplete transaction data"}), 400

    try:
        # Get a real-time prediction from the ML model
        prediction = model_provider.predict(transaction_data)

        # Add the transaction to the persistent knowledge graph
        df = pd.DataFrame([transaction_data])
        db_provider.add_transactions_from_df(df)

        # Return the result
        response = {
            "message": "Transaction processed and added to graph.",
            "transaction_id": transaction_data.get('step', 'N/A'),
            "is_suspicious": prediction.get('is_suspicious'),
            "confidence_score": prediction.get('confidence_score')
        }
        return jsonify(response), 201
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
@app.route('/api/upload-csv', methods=['POST'])
def upload_csv():
    if 'file' not in request.files or 'mapping' not in request.form:
        return jsonify({"error": "File or mapping data is missing"}), 400
    
    file = request.files['file']
    mapping_json = request.form['mapping']
    
    if file.filename == '' or not file.filename.endswith('.csv'):
        return jsonify({"error": "Invalid or missing CSV file"}), 400

    try:
        filename = werkzeug.utils.secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        df = process_uploaded_csv(filepath, mapping_json)
        if df is None:
            return jsonify({"error": "Failed to process CSV with the provided mapping."}), 400
        
        db_provider.add_transactions_from_df(df)
        return jsonify({
            "message": f"CSV '{filename}' processed, {len(df)} transactions merged.",
            "filename": filename,
            "transactions_added": len(df)
        }), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
@app.route('/api/upload-pdf', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    
    if file.filename == '' or not file.filename.endswith('.pdf'):
        return jsonify({"error": "Invalid or missing PDF file"}), 400

    try:
        filename = werkzeug.utils.secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        df = process_uploaded_pdf(filepath)
        if df is None:
            return jsonify({"error": "Failed to extract transactions from the PDF."}), 400
        
        db_provider.add_transactions_from_df(df)
        return jsonify({
            "message": f"PDF '{filename}' processed, {len(df)} transactions merged.",
            "filename": filename,
            "transactions_added": len(df)
        }), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
@app.route('/api/analyze-graph/<string:account_id>', methods=['GET'])
def analyze_account_graph(account_id):
    try:
        # Fetch the subgraph for the account from Neo4j
        graph_data = db_provider.get_transaction_graph(account_id, limit=100)
        if not graph_data or not graph_data['nodes']:
            return jsonify({"message": f"No graph data found for account {account_id}"}), 404
        
        # Get predictions for the subgraph using the GNN
        gnn_results = model_provider.predict_with_gnn(graph_data)
        
        return jsonify(gnn_results), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred during graph analysis: {str(e)}"}), 500
@app.route('/api/account-summary/<string:account_id>', methods=['GET'])
def get_account_summary(account_id):
    try:
        # Fetch transaction history from the graph database
        history_df = db_provider.get_account_history(account_id)
        if history_df is None or history_df.empty:
            return jsonify({"summary": "No transaction history found for this account."}), 404

        # Generate the summary using our model provider
        summary = model_provider.generate_summary(history_df)
        
        return jsonify({"account_id": account_id, "summary": summary}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred during summarization: {str(e)}"}), 500
