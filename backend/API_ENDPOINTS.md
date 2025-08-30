# AML Guardian API Endpoints

## Overview
This document describes all available API endpoints for the AML Guardian money laundering detection system.

## Basic Endpoints

### Transaction Upload
- **POST** `/api/upload-file`
  - Uploads and processes transaction data files (CSV/PDF)
  - Returns: Upload status and processed records count

### ML Predictions
- **POST** `/api/predict`
  - Get ML prediction for a single transaction
  - Body: Transaction data JSON
  - Returns: Prediction result with probability

### Graph Operations
- **POST** `/api/add-to-graph`
  - Add transaction data to the graph database
  - Body: Transaction data JSON
  - Returns: Graph insertion status

- **GET** `/api/suspects`
  - Get list of accounts flagged as suspicious
  - Query params: `page`, `per_page`
  - Returns: Paginated list of suspect accounts

- **GET** `/api/graph-data`
  - Get graph visualization data
  - Returns: Nodes and edges for visualization

### Investigation
- **GET** `/api/account/<account_id>/transactions`
  - Get all transactions for a specific account
  - Returns: Transaction history

- **POST** `/api/trace`
  - Trace transactions between accounts
  - Body: `{"source": "account_id", "target": "account_id"}`
  - Returns: Transaction paths and analysis

## Advanced Money Laundering Detection Endpoints

### Risk Assessment
- **GET** `/api/advanced-risk-score/<account_id>`
  - Get comprehensive risk score with detailed analysis
  - Returns: Multi-factor risk assessment
  - Risk factors: Velocity, Amount patterns, Network centrality, Geographic, Structural, Temporal, Counterparty

### Money Flow Tracking
- **GET** `/api/money-flow-tracking/<account_id>`
  - Track money flow across multiple accounts and entities
  - Query params: `max_depth` (default: 5, max: 10)
  - Returns: Money flow paths and suspicious patterns

### Layering Detection
- **GET** `/api/layering-detection/<account_id>`
  - Detect complex layering schemes and circular transactions
  - Returns: Layering patterns and circular transaction analysis

### Network Analysis
- **GET** `/api/circular-transactions`
  - Find circular money flows across the entire network
  - Query params: `min_amount` (default: 5000), `max_cycle_length` (default: 8, max: 10)
  - Returns: Detected circular transaction cycles

- **GET** `/api/shell-company-networks`
  - Identify potential shell company networks
  - Returns: Shell company network structures and indicators

- **GET** `/api/network-centrality/<account_id>`
  - Get network centrality metrics for risk assessment
  - Returns: Betweenness, closeness, degree centrality metrics

### Pattern Analysis
- **GET** `/api/cash-pattern-analysis`
  - Analyze cash-intensive transaction patterns
  - Query params: `min_amount` (default: 10000)
  - Returns: Cash transaction patterns and risk scores

- **GET** `/api/offshore-patterns`
  - Find patterns involving offshore accounts and jurisdictions
  - Returns: Offshore transaction patterns by type

### Comprehensive Analysis
- **GET** `/api/comprehensive-analysis/<account_id>`
  - Get comprehensive analysis combining all detection methods
  - Returns: Complete risk assessment with recommendations

## Response Formats

### Success Response
```json
{
  "status": "success",
  "data": {
    // Response data
  },
  "timestamp": "2024-01-01T00:00:00.000000"
}
```

### Error Response
```json
{
  "error": "Error description",
  "timestamp": "2024-01-01T00:00:00.000000"
}
```

### Risk Analysis Response
```json
{
  "account_id": "account_123",
  "risk_score": 0.75,
  "risk_level": "HIGH",
  "risk_factors": [
    {
      "name": "velocity_risk",
      "score": 0.8,
      "description": "High transaction velocity detected"
    }
  ],
  "entity_type": "INDIVIDUAL",
  "account_profile": {
    "total_transactions": 150,
    "total_volume": 1500000.00,
    "unique_counterparties": 45
  }
}
```

### Money Flow Response
```json
{
  "source_account": "account_123",
  "flow_paths": [
    {
      "path": ["account_123", "account_456", "account_789"],
      "total_amount": 50000.00,
      "transaction_count": 3,
      "risk_indicators": ["rapid_succession", "round_amounts"]
    }
  ],
  "suspicious_patterns": [
    {
      "pattern_type": "circular_flow",
      "accounts_involved": ["account_123", "account_456"],
      "risk_score": 0.85
    }
  ]
}
```

## Error Codes

- **400**: Bad Request - Invalid input data
- **404**: Not Found - Resource not found
- **500**: Internal Server Error - Server processing error

## Rate Limiting

- Standard endpoints: 100 requests per minute
- Advanced analysis endpoints: 20 requests per minute
- File upload endpoints: 10 requests per minute

## Authentication

Currently, the API does not require authentication. In production environments, implement proper authentication and authorization mechanisms.

## Security Considerations

- All inputs are validated and sanitized
- SQL/Cypher injection protection implemented
- File upload size limits enforced
- Request size limits enforced
- Comprehensive error handling

## Usage Examples

### Get Advanced Risk Score
```bash
curl -X GET "http://localhost:5001/api/advanced-risk-score/account_123"
```

### Track Money Flow
```bash
curl -X GET "http://localhost:5001/api/money-flow-tracking/account_123?max_depth=6"
```

### Find Circular Transactions
```bash
curl -X GET "http://localhost:5001/api/circular-transactions?min_amount=10000&max_cycle_length=5"
```

### Comprehensive Analysis
```bash
curl -X GET "http://localhost:5001/api/comprehensive-analysis/account_123"
```
