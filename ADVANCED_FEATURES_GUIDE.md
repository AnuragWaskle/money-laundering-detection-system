# AML Guardian Advanced Features Usage Guide

## Quick Start

### 1. Start the Enhanced System
```bash
# Navigate to backend directory
cd backend

# Start the Flask application
python app.py
```

### 2. Test Advanced Features
```bash
# Run the comprehensive test suite
python test_advanced_aml.py
```

## Advanced Feature Usage

### 1. Advanced Risk Scoring

Get comprehensive risk assessment for any account:

```bash
curl -X GET "http://localhost:5001/api/advanced-risk-score/ACC_000001"
```

**Response Example:**
```json
{
  "account_id": "ACC_000001",
  "risk_score": 0.85,
  "risk_level": "HIGH",
  "entity_type": "INDIVIDUAL",
  "risk_factors": [
    {
      "name": "velocity_risk",
      "score": 0.9,
      "weight": 0.2,
      "description": "High transaction velocity detected"
    },
    {
      "name": "amount_pattern_risk", 
      "score": 0.7,
      "weight": 0.15,
      "description": "Unusual amount patterns identified"
    }
  ],
  "account_profile": {
    "total_transactions": 156,
    "total_volume": 2450000.00,
    "unique_counterparties": 89,
    "avg_transaction_amount": 15705.13
  }
}
```

### 2. Money Flow Tracking

Track money across multiple accounts and detect suspicious patterns:

```bash
curl -X GET "http://localhost:5001/api/money-flow-tracking/ACC_000001?max_depth=5"
```

**Key Features:**
- Multi-hop transaction tracking
- Suspicious pattern detection
- Flow velocity analysis
- Cross-entity mapping

### 3. Circular Transaction Detection

Find circular money flows across the network:

```bash
curl -X GET "http://localhost:5001/api/circular-transactions?min_amount=20000&max_cycle_length=6"
```

**Detection Capabilities:**
- Multi-hop circular patterns
- Round-trip transaction analysis
- Configurable cycle parameters
- Risk scoring for each cycle

### 4. Shell Company Network Analysis

Identify potential shell company structures:

```bash
curl -X GET "http://localhost:5001/api/shell-company-networks"
```

**Analysis Features:**
- Intermediary entity detection
- Complex ownership structures
- Corporate layering schemes
- Risk indicator assessment

### 5. Layering Scheme Detection

Detect complex money laundering layering patterns:

```bash
curl -X GET "http://localhost:5001/api/layering-detection/ACC_000001"
```

**Detection Methods:**
- Multi-stage transaction analysis
- Rapid succession patterns
- Amount fragmentation detection
- Temporal pattern analysis

### 6. Cash Pattern Analysis

Analyze cash-intensive transaction patterns:

```bash
curl -X GET "http://localhost:5001/api/cash-pattern-analysis?min_amount=10000"
```

**Pattern Types:**
- Cash structuring detection
- High-volume cash analysis
- Frequency pattern analysis
- Threshold avoidance detection

### 7. Offshore Pattern Detection

Find offshore transaction patterns and high-risk jurisdictions:

```bash
curl -X GET "http://localhost:5001/api/offshore-patterns"
```

**Capabilities:**
- Cross-border transaction analysis
- Tax haven identification
- Geographic risk assessment
- Regulatory compliance patterns

### 8. Comprehensive Analysis

Get complete risk assessment with recommendations:

```bash
curl -X GET "http://localhost:5001/api/comprehensive-analysis/ACC_000001"
```

**Includes:**
- Advanced risk scoring
- Money flow tracking
- Layering detection
- Network centrality analysis
- Actionable recommendations

## Risk Factor Categories

### 1. Velocity Risk (Weight: 20%)
- **High Frequency**: Unusual transaction frequency
- **Rapid Succession**: Multiple transactions in short timeframes
- **Burst Patterns**: Concentrated transaction activity

### 2. Amount Pattern Risk (Weight: 15%)
- **Round Amounts**: Preference for round number transactions
- **Structuring**: Transactions just below reporting thresholds
- **Progressive Amounts**: Systematic amount variations

### 3. Network Centrality Risk (Weight: 20%)
- **Hub Activity**: Central position in transaction networks
- **Bridge Connections**: Connections between separate networks
- **Isolation Patterns**: Unusual network isolation

### 4. Geographic Risk (Weight: 15%)
- **High-Risk Jurisdictions**: Transactions with risky countries
- **Offshore Activity**: Offshore account interactions
- **Cross-Border Patterns**: International transaction patterns

### 5. Structural Risk (Weight: 10%)
- **Entity Type Risk**: Corporate vs individual risk profiles
- **Ownership Complexity**: Complex ownership structures
- **Shell Company Indicators**: Shell company characteristics

### 6. Temporal Risk (Weight: 10%)
- **Off-Hours Activity**: Transactions outside normal hours
- **Holiday Patterns**: Activity during holidays/weekends
- **Seasonal Anomalies**: Unusual seasonal patterns

### 7. Counterparty Risk (Weight: 10%)
- **High-Risk Associations**: Connections to high-risk entities
- **Blacklist Connections**: Links to sanctioned entities
- **Network Contamination**: Indirect high-risk connections

## Risk Level Classification

### CRITICAL (0.8-1.0)
- **Immediate Action Required**
- **SAR Filing Recommended** 
- **Enhanced Due Diligence**
- **Account Monitoring**

### HIGH (0.6-0.8)
- **Enhanced Monitoring**
- **Additional Documentation**
- **Transaction Review**
- **Compliance Review**

### MEDIUM (0.4-0.6)
- **Increased Monitoring**
- **Periodic Review**
- **Documentation Check**
- **Pattern Monitoring**

### LOW (0.0-0.4)
- **Standard Monitoring**
- **Regular Review Schedule**
- **Normal Processing**
- **Basic Compliance**

## Advanced Query Parameters

### Money Flow Tracking
- `max_depth`: Maximum hops to track (default: 5, max: 10)
- `min_amount`: Minimum transaction amount to consider
- `time_window`: Time window for analysis (days)

### Circular Transaction Detection
- `min_amount`: Minimum cycle amount (default: $5,000)
- `max_cycle_length`: Maximum cycle hops (default: 8, max: 10)
- `time_window`: Time window for cycle detection

### Cash Pattern Analysis
- `min_amount`: Minimum cash amount (default: $10,000)
- `frequency_threshold`: Minimum frequency for pattern
- `time_period`: Analysis time period (days)

## Integration Examples

### Python Integration
```python
import requests

# Get advanced risk score
response = requests.get(
    "http://localhost:5001/api/advanced-risk-score/ACC_000001"
)
risk_data = response.json()

# Check risk level
if risk_data.get('risk_level') == 'HIGH':
    print("High risk account detected!")
    
# Get recommendations
comprehensive = requests.get(
    "http://localhost:5001/api/comprehensive-analysis/ACC_000001"
)
recommendations = comprehensive.json()['overall_assessment']['recommended_actions']
```

### JavaScript Integration
```javascript
// Get money flow tracking
fetch('http://localhost:5001/api/money-flow-tracking/ACC_000001?max_depth=5')
  .then(response => response.json())
  .then(data => {
    const suspiciousPatterns = data.suspicious_patterns;
    if (suspiciousPatterns.length > 0) {
      console.log('Suspicious patterns detected:', suspiciousPatterns);
    }
  });
```

## Best Practices

### 1. Risk Assessment Workflow
1. **Initial Screening**: Use advanced risk scoring for all new accounts
2. **Pattern Analysis**: Run money flow tracking for medium+ risk accounts  
3. **Deep Investigation**: Use comprehensive analysis for high-risk cases
4. **Ongoing Monitoring**: Regular circular transaction and cash pattern checks

### 2. Performance Optimization
- Use appropriate `max_depth` parameters to balance detail vs performance
- Set reasonable `min_amount` thresholds to focus on material transactions
- Implement caching for frequently accessed accounts
- Monitor API response times and adjust parameters as needed

### 3. Compliance Integration
- Configure risk thresholds based on regulatory requirements
- Set up automated alerts for critical risk levels
- Maintain audit trails of all risk assessments
- Regular calibration of risk scoring models

### 4. Monitoring and Alerting
- Set up automated monitoring for high-risk patterns
- Implement real-time alerts for critical risk scores
- Create dashboards for ongoing surveillance
- Regular review of detection effectiveness

## Troubleshooting

### Common Issues

**High Memory Usage:**
- Reduce `max_depth` parameter for money flow tracking
- Increase `min_amount` thresholds to reduce data volume
- Implement result pagination for large datasets

**Slow API Responses:**
- Check Neo4j database performance
- Optimize graph database indexes
- Reduce analysis depth/complexity
- Monitor system resource usage

**Missing Risk Factors:**
- Ensure sufficient transaction history
- Verify data quality and completeness
- Check account relationship data
- Validate temporal data ranges

### Performance Tuning
```bash
# Check database performance
curl -X GET "http://localhost:5001/api/network-centrality/ACC_000001"

# Monitor response times
time curl -X GET "http://localhost:5001/api/comprehensive-analysis/ACC_000001"
```

## Support and Documentation

- **API Documentation**: `backend/API_ENDPOINTS.md`
- **Enhancement Summary**: `ADVANCED_ENHANCEMENT_SUMMARY.md`
- **Test Suite**: `backend/test_advanced_aml.py`
- **Configuration**: `backend/.env.example`

For additional support, review the comprehensive test suite which demonstrates all advanced features with realistic test data.
