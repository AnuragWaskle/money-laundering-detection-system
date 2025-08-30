import os
import logging
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify
from flask_cors import CORS
import werkzeug.utils
import pandas as pd

from config import Config, config_by_name
from ml_models import model_provider
from graph_db import db_provider
from utils import process_uploaded_csv, process_uploaded_pdf
from validation import (
    validate_transaction_data, 
    sanitize_transaction_data,
    clean_account_id,
    validate_pagination_params,
    SecurityError,
    require_valid_json,
    validate_request_size
)
from advanced_risk_scorer import AdvancedRiskScorer

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL, 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Load configuration
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config_by_name.get(env, config_by_name['default']))

# Setup upload folder
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Initialize advanced risk scorer
risk_scorer = AdvancedRiskScorer(db_provider)

# Validation helpers
def validate_json_request(required_fields=None):
    """Decorator to validate JSON requests"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({"error": "Content-Type must be application/json"}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({"error": "Invalid JSON data"}), 400
            
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    return jsonify({
                        "error": f"Missing required fields: {', '.join(missing_fields)}"
                    }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_file_upload(allowed_extensions):
    """Decorator to validate file uploads"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'file' not in request.files:
                return jsonify({"error": "No file provided"}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({"error": "No file selected"}), 400
            
            if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
                return jsonify({
                    "error": f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
                }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def handle_database_errors(f):
    """Decorator to handle database connection errors"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            if not db_provider.graph:
                return jsonify({
                    "error": "Database connection unavailable. Please try again later."
                }), 503
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Database error in {f.__name__}: {str(e)}")
            return jsonify({
                "error": "Database operation failed. Please try again later."
            }), 500
    return decorated_function

# Initialize database constraints with error handling
try:
    with app.app_context():
        if db_provider.graph:
            db_provider.setup_constraints()
            logger.info("Database constraints setup completed")
        else:
            logger.warning("Database connection not available during startup")
except Exception as e:
    logger.error(f"Failed to setup database constraints: {str(e)}")

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint with database status"""
    try:
        db_status = "connected" if db_provider.graph else "disconnected"
        return jsonify({
            "status": "healthy",
            "message": "Backend is running",
            "database": db_status,
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

# Transaction processing endpoints
@app.route('/api/transaction', methods=['POST'])
@require_valid_json
@validate_request_size(max_size=1024*1024)  # 1MB limit
@handle_database_errors
def handle_realtime_transaction():
    """Process real-time transaction data with comprehensive validation"""
    try:
        transaction_data = request.get_json()
        
        # Validate transaction data structure and values
        is_valid, error_msg = validate_transaction_data(transaction_data)
        if not is_valid:
            return jsonify({"error": error_msg}), 400
        
        # Sanitize the data
        sanitized_data = sanitize_transaction_data(transaction_data)
        
        # Get prediction from ML model
        prediction = model_provider.predict(sanitized_data)
        
        # Add transaction to graph database
        df = pd.DataFrame([sanitized_data])
        db_provider.add_transactions_from_df(df)
        
        response = {
            "message": "Transaction processed and added to graph",
            "transaction_id": sanitized_data.get('step', 'N/A'),
            "is_suspicious": prediction.get('is_suspicious', False),
            "confidence_score": prediction.get('confidence_score', 0.0),
            "reason": prediction.get('reason', 'Analysis completed'),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Processed transaction {response['transaction_id']}")
        return jsonify(response), 201
        
    except SecurityError as e:
        logger.warning(f"Security error in transaction processing: {str(e)}")
        return jsonify({"error": "Invalid input data"}), 400
    except Exception as e:
        logger.error(f"Error processing transaction: {str(e)}")
        return jsonify({"error": "Failed to process transaction"}), 500

# File upload endpoints
@app.route('/api/upload-csv', methods=['POST'])
@validate_file_upload(['.csv'])
@handle_database_errors
def upload_csv():
    """Upload and process CSV file"""
    try:
        if 'mapping' not in request.form:
            return jsonify({"error": "Mapping data is required"}), 400
        
        file = request.files['file']
        mapping_json = request.form['mapping']
        
        # Secure filename and save
        filename = werkzeug.utils.secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process CSV with mapping
        df = process_uploaded_csv(filepath, mapping_json)
        if df is None:
            return jsonify({"error": "Failed to process CSV with the provided mapping"}), 400
        
        # Add to database
        db_provider.add_transactions_from_df(df)
        
        # Clean up uploaded file
        try:
            os.remove(filepath)
        except OSError:
            logger.warning(f"Could not remove temporary file: {filepath}")
        
        response = {
            "message": f"CSV '{filename}' processed successfully",
            "filename": filename,
            "transactions_added": len(df),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Processed CSV file {filename} with {len(df)} transactions")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error processing CSV: {str(e)}")
        return jsonify({"error": "Failed to process CSV file"}), 500

@app.route('/api/upload-pdf', methods=['POST'])
@validate_file_upload(['.pdf'])
@handle_database_errors
def upload_pdf():
    """Upload and process PDF file"""
    try:
        file = request.files['file']
        
        # Secure filename and save
        filename = werkzeug.utils.secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process PDF
        df = process_uploaded_pdf(filepath)
        if df is None:
            return jsonify({"error": "Failed to extract transactions from PDF"}), 400
        
        # Add to database
        db_provider.add_transactions_from_df(df)
        
        # Clean up uploaded file
        try:
            os.remove(filepath)
        except OSError:
            logger.warning(f"Could not remove temporary file: {filepath}")
        
        response = {
            "message": f"PDF '{filename}' processed successfully",
            "filename": filename,
            "transactions_added": len(df),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Processed PDF file {filename} with {len(df)} transactions")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        return jsonify({"error": "Failed to process PDF file"}), 500

# Prediction and analysis endpoints
@app.route('/api/predict', methods=['POST'])
@validate_json_request()
def handle_prediction():
    """Handle prediction requests"""
    try:
        data = request.get_json()
        prediction_result = model_provider.predict(data)
        
        prediction_result["transaction_id"] = data.get("id", "N/A")
        prediction_result["timestamp"] = datetime.utcnow().isoformat()
        
        if prediction_result.get("is_suspicious"):
            confidence = prediction_result.get('confidence_score', 0)
            prediction_result["reason"] = f"Flagged with {confidence:.0%} confidence"
        else:
            prediction_result["reason"] = "Considered normal activity"
        
        return jsonify(prediction_result), 200
        
    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        return jsonify({"error": "Prediction failed"}), 500

@app.route('/api/graph-data', methods=['GET'])
@handle_database_errors
def get_graph():
    """Get graph data for an account with proper validation"""
    try:
        account_id = request.args.get('account_id')
        if not account_id:
            return jsonify({"error": "account_id parameter is required"}), 400
        
        # Clean and validate account ID
        try:
            clean_id = clean_account_id(account_id)
        except SecurityError as e:
            return jsonify({"error": str(e)}), 400
        
        # Get pagination parameters
        limit, _ = validate_pagination_params(request.args)
        
        graph_data = db_provider.get_transaction_graph(clean_id, limit=limit)
        
        if not graph_data.get("nodes"):
            return jsonify({
                "message": f"No transactions found for account '{clean_id}'",
                "nodes": [],
                "links": []
            }), 404
        
        return jsonify(graph_data), 200
        
    except Exception as e:
        logger.error(f"Error fetching graph data: {str(e)}")
        return jsonify({"error": "Failed to fetch graph data"}), 500

@app.route('/api/analyze-graph/<string:account_id>', methods=['GET'])
@handle_database_errors
def analyze_account_graph(account_id):
    """Analyze account graph using GNN with proper validation"""
    try:
        # Clean and validate account ID
        try:
            clean_id = clean_account_id(account_id)
        except SecurityError as e:
            return jsonify({"error": str(e)}), 400
        
        # Fetch subgraph from Neo4j
        graph_data = db_provider.get_transaction_graph(clean_id, limit=100)
        if not graph_data or not graph_data.get('nodes'):
            return jsonify({
                "message": f"No graph data found for account {clean_id}"
            }), 404
        
        # Get GNN predictions
        gnn_results = model_provider.predict_with_gnn(graph_data)
        gnn_results["account_id"] = clean_id
        gnn_results["timestamp"] = datetime.utcnow().isoformat()
        
        logger.info(f"Analyzed graph for account {clean_id}")
        return jsonify(gnn_results), 200
        
    except Exception as e:
        logger.error(f"Error during graph analysis: {str(e)}")
        return jsonify({"error": "Graph analysis failed"}), 500

@app.route('/api/account-summary/<string:account_id>', methods=['GET'])
@handle_database_errors
def get_account_summary(account_id):
    """Get account summary using AI"""
    try:
        if not account_id.strip():
            return jsonify({"error": "Invalid account_id"}), 400
        
        # Fetch transaction history
        history_df = db_provider.get_account_history(account_id)
        if history_df is None or history_df.empty:
            return jsonify({
                "summary": "No transaction history found for this account"
            }), 404
        
        # Generate summary
        summary = model_provider.generate_summary(history_df)
        
        response = {
            "account_id": account_id,
            "summary": summary,
            "transaction_count": len(history_df),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Generated summary for account {account_id}")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error during summarization: {str(e)}")
        return jsonify({"error": "Summary generation failed"}), 500

# Analysis endpoints
@app.route('/api/graph/find-cycles', methods=['GET'])
@handle_database_errors
def find_cycles_endpoint():
    """Find cycles in the transaction graph"""
    try:
        nodes_in_cycles = db_provider.find_all_cycles()
        return jsonify({
            "nodes": nodes_in_cycles,
            "count": len(nodes_in_cycles),
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error finding cycles: {str(e)}")
        return jsonify({"error": "Failed to find cycles"}), 500

@app.route('/api/graph/find-high-risk', methods=['GET'])
@handle_database_errors
def find_high_risk_endpoint():
    """Find high-risk nodes in the graph"""
    try:
        high_risk_nodes = db_provider.find_high_risk_nodes()
        return jsonify({
            "nodes": high_risk_nodes,
            "count": len(high_risk_nodes),
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error finding high-risk nodes: {str(e)}")
        return jsonify({"error": "Failed to find high-risk nodes"}), 500

# Dashboard endpoints
@app.route('/api/global-dashboard', methods=['GET'])
@handle_database_errors
def get_global_dashboard():
    """Get global dashboard statistics"""
    try:
        stats = {
            "total_accounts": db_provider.get_total_accounts(),
            "total_transactions": db_provider.get_total_transactions(),
            "high_risk_accounts": len(db_provider.find_high_risk_nodes()),
            "suspicious_cycles": len(db_provider.find_all_cycles()),
            "timestamp": datetime.utcnow().isoformat()
        }
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Error fetching dashboard data: {str(e)}")
        return jsonify({"error": "Failed to fetch dashboard data"}), 500

@app.route('/api/cases', methods=['GET'])
@handle_database_errors
def get_cases():
    """Get case management data"""
    try:
        high_risk_nodes = db_provider.find_high_risk_nodes()
        limit = request.args.get('limit', 20, type=int)
        
        cases = []
        for node in high_risk_nodes[:limit]:
            try:
                account_id = node.get('account_id', 'Unknown')
                risk_score = node.get('risk_score', 0)
                cases.append({
                    "case_id": f"CASE-{account_id}",
                    "account_id": account_id,
                    "risk_score": risk_score,
                    "status": "Open" if risk_score > 0.7 else "Under Review",
                    "created_date": datetime.utcnow().strftime("%Y-%m-%d")
                })
            except Exception as e:
                logger.warning(f"Error processing case for node {node}: {str(e)}")
                continue
        
        return jsonify({
            "cases": cases,
            "total_cases": len(cases),
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error fetching cases: {str(e)}")
        return jsonify({"error": "Failed to fetch cases"}), 500

@app.route('/api/trace-investigate', methods=['GET', 'POST'])
@handle_database_errors
def trace_investigate():
    """Handle trace investigation requests"""
    if request.method == 'GET':
        try:
            available_accounts = db_provider.get_all_account_ids()[:50]
            return jsonify({
                "message": "Trace investigation ready",
                "available_accounts": available_accounts,
                "account_count": len(available_accounts),
                "timestamp": datetime.utcnow().isoformat()
            }), 200
        except Exception as e:
            logger.error(f"Error getting trace data: {str(e)}")
            return jsonify({"error": "Failed to get trace data"}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Invalid JSON data"}), 400
            
            account_id = data.get('account_id')
            if not account_id:
                return jsonify({"error": "account_id is required"}), 400
            
            # Get transaction path
            trace_data = db_provider.get_transaction_path(account_id)
            if not trace_data:
                return jsonify({
                    "error": "No trace data found for this account"
                }), 404
            
            response = {
                "account_id": account_id,
                "trace_length": len(trace_data),
                "trace_data": trace_data,
                "message": "Trace analysis complete",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Completed trace investigation for account {account_id}")
            return jsonify(response), 200
            
        except Exception as e:
            logger.error(f"Error in trace investigation: {str(e)}")
            return jsonify({"error": "Trace investigation failed"}), 500

# Advanced Money Laundering Detection Endpoints
@app.route('/api/advanced-risk-score/<string:account_id>', methods=['GET'])
@handle_database_errors
def get_advanced_risk_score(account_id):
    """Get comprehensive risk score with detailed analysis"""
    try:
        # Clean and validate account ID
        try:
            clean_id = clean_account_id(account_id)
        except SecurityError as e:
            return jsonify({"error": str(e)}), 400
        
        # Calculate comprehensive risk score
        risk_analysis = risk_scorer.calculate_comprehensive_risk_score(clean_id)
        
        if "error" in risk_analysis:
            return jsonify(risk_analysis), 500
        
        logger.info(f"Generated advanced risk score for account {clean_id}")
        return jsonify(risk_analysis), 200
        
    except Exception as e:
        logger.error(f"Error calculating advanced risk score: {str(e)}")
        return jsonify({"error": "Risk analysis failed"}), 500

@app.route('/api/money-flow-tracking/<string:account_id>', methods=['GET'])
@handle_database_errors
def track_money_flow(account_id):
    """Track money flow across multiple accounts and entities"""
    try:
        # Clean and validate account ID
        try:
            clean_id = clean_account_id(account_id)
        except SecurityError as e:
            return jsonify({"error": str(e)}), 400
        
        # Get parameters
        max_depth = request.args.get('max_depth', 5, type=int)
        max_depth = min(max_depth, 10)  # Limit to prevent excessive queries
        
        # Track money flow
        flow_analysis = risk_scorer.track_money_flow(clean_id, max_depth)
        
        if "error" in flow_analysis:
            return jsonify(flow_analysis), 500
        
        logger.info(f"Tracked money flow for account {clean_id}")
        return jsonify(flow_analysis), 200
        
    except Exception as e:
        logger.error(f"Error tracking money flow: {str(e)}")
        return jsonify({"error": "Money flow tracking failed"}), 500

@app.route('/api/layering-detection/<string:account_id>', methods=['GET'])
@handle_database_errors
def detect_layering_schemes(account_id):
    """Detect complex layering schemes and circular transactions"""
    try:
        # Clean and validate account ID
        try:
            clean_id = clean_account_id(account_id)
        except SecurityError as e:
            return jsonify({"error": str(e)}), 400
        
        # Detect layering schemes
        layering_analysis = risk_scorer.detect_layering_schemes(clean_id)
        
        if "error" in layering_analysis:
            return jsonify(layering_analysis), 500
        
        logger.info(f"Analyzed layering schemes for account {clean_id}")
        return jsonify(layering_analysis), 200
        
    except Exception as e:
        logger.error(f"Error detecting layering schemes: {str(e)}")
        return jsonify({"error": "Layering detection failed"}), 500

@app.route('/api/circular-transactions', methods=['GET'])
@handle_database_errors
def find_circular_transactions():
    """Find circular money flows across the entire network"""
    try:
        # Get parameters
        min_amount = request.args.get('min_amount', 5000, type=float)
        max_cycle_length = request.args.get('max_cycle_length', 8, type=int)
        
        # Validate parameters
        min_amount = max(min_amount, 1000)  # Minimum $1000
        max_cycle_length = min(max_cycle_length, 10)  # Maximum 10 hops
        
        # Find circular transactions
        cycles = db_provider.detect_circular_transactions(min_amount, max_cycle_length)
        
        response = {
            "total_cycles": len(cycles),
            "cycles": cycles,
            "search_parameters": {
                "min_amount": min_amount,
                "max_cycle_length": max_cycle_length
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Found {len(cycles)} circular transaction patterns")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error finding circular transactions: {str(e)}")
        return jsonify({"error": "Circular transaction detection failed"}), 500

@app.route('/api/shell-company-networks', methods=['GET'])
@handle_database_errors
def find_shell_company_networks():
    """Identify potential shell company networks"""
    try:
        # Find shell company networks
        networks = db_provider.find_shell_company_networks()
        
        response = {
            "total_networks": len(networks),
            "networks": networks,
            "analysis": {
                "high_risk_networks": [n for n in networks if len(n.get('shell_indicators', [])) >= 2],
                "total_flow_volume": sum(n.get('total_flow', 0) for n in networks),
                "unique_entities": len(set(
                    entity for network in networks 
                    for entity in [network.get('source'), network.get('intermediary'), network.get('destination')]
                    if entity
                ))
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Found {len(networks)} potential shell company networks")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error finding shell company networks: {str(e)}")
        return jsonify({"error": "Shell company network detection failed"}), 500

@app.route('/api/cash-pattern-analysis', methods=['GET'])
@handle_database_errors
def analyze_cash_patterns():
    """Analyze cash-intensive transaction patterns"""
    try:
        # Get parameters
        min_cash_amount = request.args.get('min_amount', 10000, type=float)
        min_cash_amount = max(min_cash_amount, 1000)  # Minimum $1000
        
        # Analyze cash patterns
        patterns = db_provider.analyze_cash_intensive_patterns(min_cash_amount)
        
        # Calculate aggregate statistics
        total_cash_volume = sum(p.get('total_cash_out', 0) + p.get('total_cash_in', 0) for p in patterns)
        high_risk_patterns = [p for p in patterns if p.get('risk_score', 0) > 0.6]
        
        response = {
            "total_patterns": len(patterns),
            "high_risk_patterns": len(high_risk_patterns),
            "total_cash_volume": total_cash_volume,
            "patterns": patterns,
            "search_parameters": {
                "min_cash_amount": min_cash_amount
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Analyzed {len(patterns)} cash transaction patterns")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error analyzing cash patterns: {str(e)}")
        return jsonify({"error": "Cash pattern analysis failed"}), 500

@app.route('/api/offshore-patterns', methods=['GET'])
@handle_database_errors
def find_offshore_patterns():
    """Find patterns involving offshore accounts and jurisdictions"""
    try:
        # Find offshore patterns
        patterns = db_provider.find_offshore_connection_patterns()
        
        # Analyze patterns
        total_offshore_volume = sum(p.get('amount', 0) for p in patterns)
        by_pattern_type = {}
        
        for pattern in patterns:
            pattern_type = pattern.get('pattern_type', 'unknown')
            if pattern_type not in by_pattern_type:
                by_pattern_type[pattern_type] = []
            by_pattern_type[pattern_type].append(pattern)
        
        response = {
            "total_patterns": len(patterns),
            "total_offshore_volume": total_offshore_volume,
            "pattern_breakdown": {
                pattern_type: {
                    "count": len(pattern_list),
                    "total_volume": sum(p.get('amount', 0) for p in pattern_list)
                }
                for pattern_type, pattern_list in by_pattern_type.items()
            },
            "patterns": patterns,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Found {len(patterns)} offshore transaction patterns")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error finding offshore patterns: {str(e)}")
        return jsonify({"error": "Offshore pattern analysis failed"}), 500

@app.route('/api/network-centrality/<string:account_id>', methods=['GET'])
@handle_database_errors
def get_network_centrality(account_id):
    """Get network centrality metrics for risk assessment"""
    try:
        # Clean and validate account ID
        try:
            clean_id = clean_account_id(account_id)
        except SecurityError as e:
            return jsonify({"error": str(e)}), 400
        
        # Calculate centrality metrics
        centrality_metrics = db_provider.calculate_account_centrality_metrics(clean_id)
        
        if not centrality_metrics:
            return jsonify({
                "message": f"No network data found for account {clean_id}"
            }), 404
        
        # Add timestamp
        centrality_metrics["timestamp"] = datetime.utcnow().isoformat()
        
        logger.info(f"Calculated centrality metrics for account {clean_id}")
        return jsonify(centrality_metrics), 200
        
    except Exception as e:
        logger.error(f"Error calculating network centrality: {str(e)}")
        return jsonify({"error": "Network centrality calculation failed"}), 500

@app.route('/api/comprehensive-analysis/<string:account_id>', methods=['GET'])
@handle_database_errors
def get_comprehensive_analysis(account_id):
    """Get comprehensive analysis combining all detection methods"""
    try:
        # Clean and validate account ID
        try:
            clean_id = clean_account_id(account_id)
        except SecurityError as e:
            return jsonify({"error": str(e)}), 400
        
        # Perform comprehensive analysis
        risk_analysis = risk_scorer.calculate_comprehensive_risk_score(clean_id)
        money_flow = risk_scorer.track_money_flow(clean_id, max_depth=4)
        layering_analysis = risk_scorer.detect_layering_schemes(clean_id)
        centrality_metrics = db_provider.calculate_account_centrality_metrics(clean_id)
        
        # Compile comprehensive report
        comprehensive_report = {
            "account_id": clean_id,
            "risk_analysis": risk_analysis,
            "money_flow_tracking": money_flow,
            "layering_detection": layering_analysis,
            "network_centrality": centrality_metrics,
            "overall_assessment": {
                "risk_level": risk_analysis.get("risk_level", "UNKNOWN"),
                "risk_score": risk_analysis.get("risk_score", 0.0),
                "key_concerns": _extract_key_concerns(risk_analysis, money_flow, layering_analysis),
                "recommended_actions": _generate_recommendations(risk_analysis)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Generated comprehensive analysis for account {clean_id}")
        return jsonify(comprehensive_report), 200
        
    except Exception as e:
        logger.error(f"Error in comprehensive analysis: {str(e)}")
        return jsonify({"error": "Comprehensive analysis failed"}), 500

def _extract_key_concerns(risk_analysis, money_flow, layering_analysis):
    """Extract key concerns from analysis results"""
    concerns = []
    
    # Extract from risk analysis
    if risk_analysis.get("risk_score", 0) > 0.7:
        concerns.append("High overall risk score")
    
    risk_factors = risk_analysis.get("risk_factors", [])
    high_risk_factors = [f for f in risk_factors if f.get("score", 0) > 0.6]
    for factor in high_risk_factors:
        concerns.append(f"High {factor.get('name', 'unknown')} risk")
    
    # Extract from money flow
    suspicious_patterns = money_flow.get("suspicious_patterns", [])
    if suspicious_patterns:
        concerns.append(f"{len(suspicious_patterns)} suspicious money flow patterns")
    
    # Extract from layering analysis
    cycles_detected = layering_analysis.get("cycles_detected", 0)
    if cycles_detected > 0:
        concerns.append(f"{cycles_detected} circular transaction patterns detected")
    
    return concerns

def _generate_recommendations(risk_analysis):
    """Generate recommendations based on risk analysis"""
    recommendations = []
    
    risk_score = risk_analysis.get("risk_score", 0)
    risk_level = risk_analysis.get("risk_level", "LOW")
    
    if risk_score > 0.8:
        recommendations.extend([
            "Immediate manual review required",
            "Consider filing SAR (Suspicious Activity Report)",
            "Enhanced due diligence recommended"
        ])
    elif risk_score > 0.6:
        recommendations.extend([
            "Enhanced monitoring recommended",
            "Additional documentation required",
            "Review transaction patterns"
        ])
    elif risk_score > 0.3:
        recommendations.extend([
            "Continued monitoring",
            "Periodic review of activity"
        ])
    else:
        recommendations.append("Standard monitoring sufficient")
    
    return recommendations

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405

@app.errorhandler(413)
def too_large(error):
    return jsonify({"error": "File too large"}), 413

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting AML Guardian backend on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
