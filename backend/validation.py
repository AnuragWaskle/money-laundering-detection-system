"""
Input validation and security utilities for the AML Guardian backend
"""
import re
import logging
from typing import Dict, List, Any, Optional
from functools import wraps
from flask import request, jsonify

logger = logging.getLogger(__name__)

# Security patterns and limits
ACCOUNT_ID_PATTERN = re.compile(r'^[A-Za-z0-9_-]{1,50}$')
ALLOWED_TRANSACTION_TYPES = {'CASH_IN', 'CASH_OUT', 'TRANSFER', 'PAYMENT', 'DEBIT'}
MAX_AMOUNT = 1_000_000_000  # 1 billion
MIN_AMOUNT = 0.01
MAX_STEP = 1_000_000
MAX_STRING_LENGTH = 100

def validate_account_id(account_id: str) -> bool:
    """Validate account ID format"""
    if not account_id or not isinstance(account_id, str):
        return False
    return bool(ACCOUNT_ID_PATTERN.match(account_id))

def validate_transaction_data(data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """Validate transaction data structure and values"""
    try:
        # Check required fields
        required_fields = ['step', 'type', 'amount', 'nameOrig', 'nameDest']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        # Validate step
        step = data.get('step')
        if not isinstance(step, (int, float)) or step < 1 or step > MAX_STEP:
            return False, f"Invalid step value: must be between 1 and {MAX_STEP}"
        
        # Validate transaction type
        tx_type = data.get('type', '').upper()
        if tx_type not in ALLOWED_TRANSACTION_TYPES:
            return False, f"Invalid transaction type: {tx_type}"
        
        # Validate amount
        amount = data.get('amount')
        if not isinstance(amount, (int, float)) or amount < MIN_AMOUNT or amount > MAX_AMOUNT:
            return False, f"Invalid amount: must be between {MIN_AMOUNT} and {MAX_AMOUNT}"
        
        # Validate account IDs
        name_orig = data.get('nameOrig', '')
        name_dest = data.get('nameDest', '')
        
        if not validate_account_id(name_orig):
            return False, f"Invalid origin account ID: {name_orig}"
        
        if not validate_account_id(name_dest):
            return False, f"Invalid destination account ID: {name_dest}"
        
        if name_orig == name_dest:
            return False, "Origin and destination accounts cannot be the same"
        
        # Validate optional fields if present
        optional_fields = ['oldbalanceOrg', 'newbalanceOrig', 'oldbalanceDest', 'newbalanceDest']
        for field in optional_fields:
            if field in data:
                value = data[field]
                if not isinstance(value, (int, float)) or value < 0 or value > MAX_AMOUNT:
                    return False, f"Invalid {field}: must be between 0 and {MAX_AMOUNT}"
        
        return True, None
        
    except Exception as e:
        logger.error(f"Error validating transaction data: {e}")
        return False, "Validation error occurred"

def sanitize_string(value: str, max_length: int = MAX_STRING_LENGTH) -> str:
    """Sanitize string input"""
    if not isinstance(value, str):
        return str(value)[:max_length]
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\'\\\x00-\x1f\x7f-\x9f]', '', value)
    return sanitized[:max_length].strip()

def validate_file_size(file_size: int, max_size: int = 16 * 1024 * 1024) -> bool:
    """Validate file size (default 16MB)"""
    return 0 < file_size <= max_size

def validate_pagination_params(request_args: Dict[str, Any]) -> tuple[int, int]:
    """Validate and return pagination parameters"""
    try:
        limit = int(request_args.get('limit', 50))
        offset = int(request_args.get('offset', 0))
        
        # Ensure reasonable limits
        limit = max(1, min(limit, 1000))
        offset = max(0, offset)
        
        return limit, offset
    except (ValueError, TypeError):
        return 50, 0

def rate_limit_key(user_id: str = None) -> str:
    """Generate rate limiting key"""
    if user_id:
        return f"rate_limit:user:{user_id}"
    return f"rate_limit:ip:{request.remote_addr}"

class SecurityError(Exception):
    """Custom exception for security-related errors"""
    pass

def require_valid_json(f):
    """Decorator to ensure request contains valid JSON"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        try:
            data = request.get_json()
            if data is None:
                return jsonify({"error": "Invalid JSON data"}), 400
        except Exception as e:
            logger.warning(f"JSON parsing error: {e}")
            return jsonify({"error": "Invalid JSON format"}), 400
        
        return f(*args, **kwargs)
    return decorated_function

def validate_request_size(max_size: int = 1024 * 1024):  # 1MB default
    """Decorator to validate request size"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.content_length and request.content_length > max_size:
                return jsonify({"error": "Request too large"}), 413
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# SQL injection prevention patterns
SQL_INJECTION_PATTERNS = [
    r"(\s*(union|select|insert|update|delete|drop|create|alter|exec|execute)\s+)",
    r"(\s*(;|--|/\*|\*/|xp_|sp_)\s*)",
    r"(\s*(script|javascript|vbscript|onload|onerror|onclick)\s*)",
]

def contains_sql_injection(text: str) -> bool:
    """Check if text contains potential SQL injection"""
    if not isinstance(text, str):
        return False
    
    text_lower = text.lower()
    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return True
    return False

def validate_cypher_injection(text: str) -> bool:
    """Check for potential Cypher injection patterns"""
    if not isinstance(text, str):
        return True
    
    # Basic Cypher injection patterns
    dangerous_patterns = [
        r'\s*;\s*match\s+',
        r'\s*;\s*create\s+',
        r'\s*;\s*delete\s+',
        r'\s*;\s*drop\s+',
        r'\s*}\s*{\s*',
        r'//.*$',  # Comments
    ]
    
    text_lower = text.lower()
    for pattern in dangerous_patterns:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return False
    return True

def clean_account_id(account_id: str) -> str:
    """Clean and validate account ID"""
    if not account_id:
        raise SecurityError("Account ID cannot be empty")
    
    # Remove whitespace
    cleaned = account_id.strip()
    
    # Check for injection attempts
    if not validate_cypher_injection(cleaned):
        raise SecurityError("Invalid characters in account ID")
    
    if contains_sql_injection(cleaned):
        raise SecurityError("Invalid characters in account ID")
    
    # Validate format
    if not validate_account_id(cleaned):
        raise SecurityError("Invalid account ID format")
    
    return cleaned

# Input sanitization functions
def sanitize_transaction_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize transaction data"""
    sanitized = {}
    
    # Copy and validate numeric fields
    numeric_fields = ['step', 'amount', 'oldbalanceOrg', 'newbalanceOrig', 'oldbalanceDest', 'newbalanceDest']
    for field in numeric_fields:
        if field in data:
            try:
                sanitized[field] = float(data[field])
            except (ValueError, TypeError):
                raise SecurityError(f"Invalid numeric value for {field}")
    
    # Sanitize string fields
    string_fields = ['type', 'nameOrig', 'nameDest']
    for field in string_fields:
        if field in data:
            sanitized[field] = sanitize_string(data[field])
    
    # Handle boolean fields
    if 'isFraud' in data:
        sanitized['isFraud'] = bool(data['isFraud'])
    
    if 'isFlaggedFraud' in data:
        sanitized['isFlaggedFraud'] = bool(data['isFlaggedFraud'])
    
    return sanitized
