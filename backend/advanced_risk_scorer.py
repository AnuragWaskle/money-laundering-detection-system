"""
Advanced Risk Scoring and Money Laundering Detection Module
Tracks money across multiple accounts, offshore entities, shell companies, and complex patterns
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import networkx as nx
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    """Risk level enumeration"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class EntityType(Enum):
    """Entity type classification"""
    INDIVIDUAL = "INDIVIDUAL"
    CORPORATE = "CORPORATE"
    SHELL_COMPANY = "SHELL_COMPANY"
    OFFSHORE_ENTITY = "OFFSHORE_ENTITY"
    FINANCIAL_INSTITUTION = "FINANCIAL_INSTITUTION"
    CRYPTOCURRENCY_EXCHANGE = "CRYPTOCURRENCY_EXCHANGE"
    UNKNOWN = "UNKNOWN"

@dataclass
class RiskFactor:
    """Individual risk factor with weight and description"""
    name: str
    score: float
    weight: float
    description: str
    evidence: List[str]

@dataclass
class AccountProfile:
    """Enhanced account profile with risk indicators"""
    account_id: str
    entity_type: EntityType
    country_code: str
    is_pep: bool = False  # Politically Exposed Person
    is_sanctioned: bool = False
    creation_date: Optional[datetime] = None
    total_inflow: float = 0.0
    total_outflow: float = 0.0
    transaction_count: int = 0
    unique_counterparties: int = 0
    risk_factors: List[RiskFactor] = None
    
    def __post_init__(self):
        if self.risk_factors is None:
            self.risk_factors = []

class AdvancedRiskScorer:
    """Advanced risk scoring engine for money laundering detection"""
    
    def __init__(self, db_provider):
        self.db_provider = db_provider
        self.offshore_countries = {
            'BM', 'KY', 'VI', 'BS', 'PA', 'LI', 'MC', 'AD', 'SM', 'MT',
            'CY', 'LU', 'CH', 'SG', 'HK', 'MY', 'TH', 'PH', 'VU', 'WS'
        }
        self.high_risk_countries = {
            'AF', 'IQ', 'IR', 'KP', 'MM', 'SO', 'SY', 'YE', 'VE', 'CU'
        }
        
        # Risk weights for different factors
        self.risk_weights = {
            'velocity': 0.15,           # Transaction velocity
            'amount_pattern': 0.20,     # Unusual amount patterns
            'network_centrality': 0.15, # Position in transaction network
            'geographic': 0.10,         # Geographic risk
            'structural': 0.15,         # Structural indicators
            'temporal': 0.10,           # Time-based patterns
            'counterparty': 0.15        # Counterparty risk
        }
    
    def calculate_comprehensive_risk_score(self, account_id: str) -> Dict:
        """Calculate comprehensive risk score for an account"""
        try:
            # Get account profile and transaction data
            profile = self._build_account_profile(account_id)
            transactions = self._get_account_transactions(account_id)
            
            if not transactions:
                return {"risk_score": 0.0, "risk_level": RiskLevel.LOW, "factors": []}
            
            # Calculate individual risk factors
            risk_factors = []
            
            # 1. Velocity Risk - Rapid transaction frequency
            velocity_risk = self._calculate_velocity_risk(transactions)
            risk_factors.append(velocity_risk)
            
            # 2. Amount Pattern Risk - Structuring, round amounts
            amount_risk = self._calculate_amount_pattern_risk(transactions)
            risk_factors.append(amount_risk)
            
            # 3. Network Centrality Risk - Position in money flow network
            network_risk = self._calculate_network_centrality_risk(account_id)
            risk_factors.append(network_risk)
            
            # 4. Geographic Risk - Offshore/high-risk jurisdictions
            geo_risk = self._calculate_geographic_risk(profile, transactions)
            risk_factors.append(geo_risk)
            
            # 5. Structural Risk - Shell company patterns
            structural_risk = self._calculate_structural_risk(profile, account_id)
            risk_factors.append(structural_risk)
            
            # 6. Temporal Risk - Unusual timing patterns
            temporal_risk = self._calculate_temporal_risk(transactions)
            risk_factors.append(temporal_risk)
            
            # 7. Counterparty Risk - High-risk associations
            counterparty_risk = self._calculate_counterparty_risk(account_id, transactions)
            risk_factors.append(counterparty_risk)
            
            # Calculate weighted risk score
            total_score = sum(
                factor.score * self.risk_weights.get(factor.name, 0.1) 
                for factor in risk_factors
            )
            
            # Normalize to 0-1 scale
            normalized_score = min(total_score, 1.0)
            
            # Determine risk level
            risk_level = self._determine_risk_level(normalized_score)
            
            return {
                "account_id": account_id,
                "risk_score": normalized_score,
                "risk_level": risk_level,
                "risk_factors": [
                    {
                        "name": factor.name,
                        "score": factor.score,
                        "weight": factor.weight,
                        "description": factor.description,
                        "evidence": factor.evidence
                    }
                    for factor in risk_factors
                ],
                "profile": {
                    "entity_type": profile.entity_type.value,
                    "country_code": profile.country_code,
                    "is_pep": profile.is_pep,
                    "is_sanctioned": profile.is_sanctioned,
                    "total_inflow": profile.total_inflow,
                    "total_outflow": profile.total_outflow,
                    "transaction_count": profile.transaction_count
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating risk score for {account_id}: {e}")
            return {"risk_score": 0.0, "risk_level": RiskLevel.LOW, "error": str(e)}
    
    def track_money_flow(self, account_id: str, max_depth: int = 5) -> Dict:
        """Track money flow across multiple accounts and entities"""
        try:
            flow_graph = self._build_money_flow_graph(account_id, max_depth)
            
            # Analyze flow patterns
            analysis = {
                "source_account": account_id,
                "total_depth": max_depth,
                "flow_analysis": self._analyze_flow_patterns(flow_graph),
                "suspicious_patterns": self._detect_suspicious_patterns(flow_graph),
                "entity_analysis": self._analyze_entities_in_flow(flow_graph),
                "geographic_analysis": self._analyze_geographic_flow(flow_graph),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error tracking money flow for {account_id}: {e}")
            return {"error": str(e)}
    
    def detect_layering_schemes(self, account_id: str) -> Dict:
        """Detect complex layering schemes and circular transactions"""
        try:
            # Find all paths and cycles involving the account
            cycles = self._find_complex_cycles(account_id)
            layering_patterns = self._detect_layering_patterns(account_id)
            
            return {
                "account_id": account_id,
                "cycles_detected": len(cycles),
                "cycle_details": cycles[:10],  # Top 10 cycles
                "layering_patterns": layering_patterns,
                "risk_assessment": self._assess_layering_risk(cycles, layering_patterns),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error detecting layering schemes for {account_id}: {e}")
            return {"error": str(e)}
    
    def _build_account_profile(self, account_id: str) -> AccountProfile:
        """Build comprehensive account profile"""
        # Extract country code and entity type from account ID patterns
        country_code = self._extract_country_code(account_id)
        entity_type = self._classify_entity_type(account_id)
        
        # Get transaction statistics
        stats = self._get_transaction_statistics(account_id)
        
        return AccountProfile(
            account_id=account_id,
            entity_type=entity_type,
            country_code=country_code,
            is_pep=self._check_pep_status(account_id),
            is_sanctioned=self._check_sanctions_list(account_id),
            total_inflow=stats.get('total_inflow', 0.0),
            total_outflow=stats.get('total_outflow', 0.0),
            transaction_count=stats.get('transaction_count', 0),
            unique_counterparties=stats.get('unique_counterparties', 0)
        )
    
    def _get_account_transactions(self, account_id: str) -> pd.DataFrame:
        """Get recent transactions for an account"""
        return self.db_provider.get_account_history(account_id, limit=1000)
    
    def _calculate_velocity_risk(self, transactions: pd.DataFrame) -> RiskFactor:
        """Calculate transaction velocity risk"""
        if transactions.empty:
            return RiskFactor("velocity", 0.0, 0.15, "No transactions", [])
        
        # Calculate transactions per day
        transactions['date'] = pd.to_datetime(transactions.get('timestamp', 0), unit='s', errors='coerce')
        daily_counts = transactions.groupby(transactions['date'].dt.date).size()
        avg_daily_tx = daily_counts.mean()
        max_daily_tx = daily_counts.max()
        
        evidence = []
        score = 0.0
        
        # High frequency scoring
        if avg_daily_tx > 50:
            score += 0.4
            evidence.append(f"High average daily transactions: {avg_daily_tx:.1f}")
        
        if max_daily_tx > 100:
            score += 0.3
            evidence.append(f"Peak daily transactions: {max_daily_tx}")
        
        # Burst detection
        if max_daily_tx > avg_daily_tx * 5:
            score += 0.3
            evidence.append("Unusual transaction bursts detected")
        
        return RiskFactor(
            "velocity", 
            min(score, 1.0), 
            0.15, 
            "Transaction frequency and velocity patterns",
            evidence
        )
    
    def _calculate_amount_pattern_risk(self, transactions: pd.DataFrame) -> RiskFactor:
        """Calculate risk based on amount patterns (structuring, round amounts)"""
        if transactions.empty:
            return RiskFactor("amount_pattern", 0.0, 0.20, "No transactions", [])
        
        amounts = transactions['amount'].values
        evidence = []
        score = 0.0
        
        # Structuring detection (amounts just below reporting thresholds)
        structuring_thresholds = [10000, 5000, 3000]
        for threshold in structuring_thresholds:
            near_threshold = np.sum((amounts >= threshold * 0.9) & (amounts < threshold))
            if near_threshold > 5:
                score += 0.3
                evidence.append(f"{near_threshold} transactions near ${threshold} threshold")
        
        # Round amount analysis
        round_amounts = np.sum(amounts % 1000 == 0)
        if round_amounts / len(amounts) > 0.5:
            score += 0.2
            evidence.append(f"High percentage of round amounts: {round_amounts/len(amounts)*100:.1f}%")
        
        # Unusual amount patterns
        amount_variance = np.var(amounts)
        amount_mean = np.mean(amounts)
        if amount_variance > amount_mean * 100:
            score += 0.2
            evidence.append("High variance in transaction amounts")
        
        # Smurfing detection (many small similar amounts)
        amount_bins = np.histogram(amounts, bins=50)[0]
        if np.max(amount_bins) > len(amounts) * 0.3:
            score += 0.3
            evidence.append("Potential smurfing pattern detected")
        
        return RiskFactor(
            "amount_pattern",
            min(score, 1.0),
            0.20,
            "Analysis of transaction amount patterns for structuring",
            evidence
        )
    
    def _calculate_network_centrality_risk(self, account_id: str) -> RiskFactor:
        """Calculate risk based on network position"""
        try:
            # Build transaction network
            network_data = self.db_provider.get_transaction_graph(account_id, limit=500)
            
            if not network_data.get('nodes') or not network_data.get('links'):
                return RiskFactor("network_centrality", 0.0, 0.15, "Insufficient network data", [])
            
            # Create NetworkX graph
            G = nx.DiGraph()
            
            # Add nodes
            for node in network_data['nodes']:
                G.add_node(node['id'])
            
            # Add edges with weights
            for link in network_data['links']:
                G.add_edge(link['source'], link['target'], weight=link.get('amount', 1))
            
            evidence = []
            score = 0.0
            
            if account_id in G:
                # Calculate centrality measures
                betweenness = nx.betweenness_centrality(G)
                closeness = nx.closeness_centrality(G)
                degree = dict(G.degree())
                
                account_betweenness = betweenness.get(account_id, 0)
                account_closeness = closeness.get(account_id, 0)
                account_degree = degree.get(account_id, 0)
                
                # High betweenness suggests intermediary role
                if account_betweenness > 0.1:
                    score += 0.4
                    evidence.append(f"High betweenness centrality: {account_betweenness:.3f}")
                
                # High closeness suggests central position
                if account_closeness > 0.5:
                    score += 0.3
                    evidence.append(f"High closeness centrality: {account_closeness:.3f}")
                
                # High degree suggests hub activity
                if account_degree > 20:
                    score += 0.3
                    evidence.append(f"High degree centrality: {account_degree}")
            
            return RiskFactor(
                "network_centrality",
                min(score, 1.0),
                0.15,
                "Position and influence in transaction network",
                evidence
            )
            
        except Exception as e:
            logger.error(f"Error calculating network centrality: {e}")
            return RiskFactor("network_centrality", 0.0, 0.15, "Network analysis failed", [])
    
    def _calculate_geographic_risk(self, profile: AccountProfile, transactions: pd.DataFrame) -> RiskFactor:
        """Calculate geographic risk factors"""
        evidence = []
        score = 0.0
        
        # Check if account is in offshore jurisdiction
        if profile.country_code in self.offshore_countries:
            score += 0.5
            evidence.append(f"Account in offshore jurisdiction: {profile.country_code}")
        
        # Check if account is in high-risk country
        if profile.country_code in self.high_risk_countries:
            score += 0.7
            evidence.append(f"Account in high-risk country: {profile.country_code}")
        
        # Analyze counterparty countries from transactions
        if not transactions.empty and 'other_party' in transactions.columns:
            counterparty_countries = set()
            for party in transactions['other_party'].unique():
                country = self._extract_country_code(party)
                if country:
                    counterparty_countries.add(country)
            
            # Check for transactions with offshore entities
            offshore_counterparties = counterparty_countries.intersection(self.offshore_countries)
            if offshore_counterparties:
                score += 0.3 * len(offshore_counterparties) / len(counterparty_countries)
                evidence.append(f"Transactions with offshore entities: {list(offshore_counterparties)}")
            
            # Check for high-risk country interactions
            high_risk_counterparties = counterparty_countries.intersection(self.high_risk_countries)
            if high_risk_counterparties:
                score += 0.4 * len(high_risk_counterparties) / len(counterparty_countries)
                evidence.append(f"Transactions with high-risk countries: {list(high_risk_counterparties)}")
        
        return RiskFactor(
            "geographic",
            min(score, 1.0),
            0.10,
            "Geographic risk based on jurisdictions involved",
            evidence
        )
    
    def _calculate_structural_risk(self, profile: AccountProfile, account_id: str) -> RiskFactor:
        """Calculate structural risk indicators for shell companies"""
        evidence = []
        score = 0.0
        
        # Check entity type
        if profile.entity_type == EntityType.SHELL_COMPANY:
            score += 0.8
            evidence.append("Identified as shell company")
        elif profile.entity_type == EntityType.OFFSHORE_ENTITY:
            score += 0.6
            evidence.append("Identified as offshore entity")
        
        # Account ID pattern analysis for shell company indicators
        shell_patterns = ['LLC', 'LTD', 'INC', 'CORP', 'HOLDING', 'INVEST', 'CAPITAL']
        if any(pattern in account_id.upper() for pattern in shell_patterns):
            score += 0.3
            evidence.append("Account name suggests corporate structure")
        
        # Check for minimal transaction history (shell companies often have sparse activity)
        if profile.transaction_count < 10 and profile.total_outflow > 100000:
            score += 0.4
            evidence.append("High-value, low-frequency transaction pattern")
        
        # Check for pass-through behavior (similar inflow and outflow)
        if profile.total_inflow > 0 and profile.total_outflow > 0:
            ratio = min(profile.total_inflow, profile.total_outflow) / max(profile.total_inflow, profile.total_outflow)
            if ratio > 0.9:
                score += 0.5
                evidence.append("Pass-through transaction pattern detected")
        
        return RiskFactor(
            "structural",
            min(score, 1.0),
            0.15,
            "Structural indicators of shell companies and pass-through entities",
            evidence
        )
    
    def _calculate_temporal_risk(self, transactions: pd.DataFrame) -> RiskFactor:
        """Calculate temporal risk patterns"""
        if transactions.empty:
            return RiskFactor("temporal", 0.0, 0.10, "No transactions", [])
        
        evidence = []
        score = 0.0
        
        # Convert timestamps
        transactions['datetime'] = pd.to_datetime(transactions.get('timestamp', 0), unit='s', errors='coerce')
        transactions['hour'] = transactions['datetime'].dt.hour
        transactions['weekday'] = transactions['datetime'].dt.weekday
        
        # Unusual time patterns
        night_transactions = np.sum((transactions['hour'] >= 22) | (transactions['hour'] <= 6))
        if night_transactions / len(transactions) > 0.3:
            score += 0.3
            evidence.append(f"High percentage of night transactions: {night_transactions/len(transactions)*100:.1f}%")
        
        # Weekend activity
        weekend_transactions = np.sum(transactions['weekday'] >= 5)
        if weekend_transactions / len(transactions) > 0.4:
            score += 0.2
            evidence.append(f"High weekend activity: {weekend_transactions/len(transactions)*100:.1f}%")
        
        # Rapid sequences
        time_diffs = transactions['datetime'].diff().dt.total_seconds()
        rapid_sequences = np.sum(time_diffs < 60)  # Transactions within 1 minute
        if rapid_sequences > 10:
            score += 0.4
            evidence.append(f"Rapid transaction sequences detected: {rapid_sequences}")
        
        # Regular patterns (may indicate automated activity)
        if len(transactions) > 50:
            hourly_variance = np.var(np.bincount(transactions['hour'], minlength=24))
            if hourly_variance < 2:  # Very regular timing
                score += 0.3
                evidence.append("Highly regular transaction timing pattern")
        
        return RiskFactor(
            "temporal",
            min(score, 1.0),
            0.10,
            "Temporal patterns in transaction timing",
            evidence
        )
    
    def _calculate_counterparty_risk(self, account_id: str, transactions: pd.DataFrame) -> RiskFactor:
        """Calculate counterparty risk"""
        if transactions.empty:
            return RiskFactor("counterparty", 0.0, 0.15, "No transactions", [])
        
        evidence = []
        score = 0.0
        
        # Get unique counterparties
        counterparties = transactions['other_party'].unique()
        
        # Check for high-risk counterparties
        high_risk_counterparties = []
        for party in counterparties:
            # Check if counterparty has shell company indicators
            if self._is_potential_shell_company(party):
                high_risk_counterparties.append(party)
        
        if high_risk_counterparties:
            score += 0.4 * len(high_risk_counterparties) / len(counterparties)
            evidence.append(f"Transactions with potential shell companies: {len(high_risk_counterparties)}")
        
        # Check for cryptocurrency exchanges
        crypto_indicators = ['EXCHANGE', 'CRYPTO', 'BTC', 'ETH', 'COIN']
        crypto_counterparties = [
            party for party in counterparties 
            if any(indicator in party.upper() for indicator in crypto_indicators)
        ]
        
        if crypto_counterparties:
            score += 0.3
            evidence.append(f"Cryptocurrency exchange transactions: {len(crypto_counterparties)}")
        
        # Check for concentration (few counterparties, high volume)
        if len(counterparties) < 5 and len(transactions) > 50:
            score += 0.3
            evidence.append("High transaction concentration with few counterparties")
        
        return RiskFactor(
            "counterparty",
            min(score, 1.0),
            0.15,
            "Risk assessment of transaction counterparties",
            evidence
        )
    
    def _determine_risk_level(self, score: float) -> RiskLevel:
        """Determine risk level based on score"""
        if score >= 0.8:
            return RiskLevel.CRITICAL
        elif score >= 0.6:
            return RiskLevel.HIGH
        elif score >= 0.3:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    # Helper methods
    def _extract_country_code(self, account_id: str) -> str:
        """Extract country code from account ID"""
        # Simple pattern matching - in real implementation, use a proper mapping
        if len(account_id) >= 2:
            return account_id[:2].upper()
        return "XX"
    
    def _classify_entity_type(self, account_id: str) -> EntityType:
        """Classify entity type based on account patterns"""
        account_upper = account_id.upper()
        
        if any(pattern in account_upper for pattern in ['SHELL', 'HOLDING', 'SPV']):
            return EntityType.SHELL_COMPANY
        elif any(pattern in account_upper for pattern in ['OFFSHORE', 'BVI', 'CAYMAN']):
            return EntityType.OFFSHORE_ENTITY
        elif any(pattern in account_upper for pattern in ['BANK', 'CREDIT', 'FINANCE']):
            return EntityType.FINANCIAL_INSTITUTION
        elif any(pattern in account_upper for pattern in ['CORP', 'LLC', 'LTD', 'INC']):
            return EntityType.CORPORATE
        elif any(pattern in account_upper for pattern in ['EXCHANGE', 'CRYPTO', 'COIN']):
            return EntityType.CRYPTOCURRENCY_EXCHANGE
        else:
            return EntityType.INDIVIDUAL
    
    def _get_transaction_statistics(self, account_id: str) -> Dict:
        """Get transaction statistics for an account"""
        try:
            transactions = self.db_provider.get_account_history(account_id, limit=1000)
            
            if transactions.empty:
                return {"total_inflow": 0, "total_outflow": 0, "transaction_count": 0, "unique_counterparties": 0}
            
            inflow = transactions[transactions['direction'] == 'incoming']['amount'].sum()
            outflow = transactions[transactions['direction'] == 'outgoing']['amount'].sum()
            
            return {
                "total_inflow": float(inflow),
                "total_outflow": float(outflow),
                "transaction_count": len(transactions),
                "unique_counterparties": transactions['other_party'].nunique()
            }
        except Exception as e:
            logger.error(f"Error getting transaction statistics: {e}")
            return {"total_inflow": 0, "total_outflow": 0, "transaction_count": 0, "unique_counterparties": 0}
    
    def _check_pep_status(self, account_id: str) -> bool:
        """Check if account belongs to a Politically Exposed Person"""
        # In real implementation, check against PEP database
        pep_indicators = ['MINISTER', 'SENATOR', 'MAYOR', 'GOVERNOR', 'AMBASSADOR']
        return any(indicator in account_id.upper() for indicator in pep_indicators)
    
    def _check_sanctions_list(self, account_id: str) -> bool:
        """Check if account is on sanctions list"""
        # In real implementation, check against OFAC/UN sanctions lists
        return False
    
    def _is_potential_shell_company(self, account_id: str) -> bool:
        """Check if account shows shell company characteristics"""
        shell_indicators = ['SHELL', 'HOLDING', 'SPV', 'INVEST', 'CAPITAL', 'MANAGEMENT']
        return any(indicator in account_id.upper() for indicator in shell_indicators)
    
    def _build_money_flow_graph(self, account_id: str, max_depth: int) -> nx.DiGraph:
        """Build a money flow graph starting from an account"""
        # This would implement BFS/DFS to trace money flows
        # Placeholder implementation
        return nx.DiGraph()
    
    def _analyze_flow_patterns(self, flow_graph: nx.DiGraph) -> Dict:
        """Analyze patterns in money flow graph"""
        return {"placeholder": "flow_analysis"}
    
    def _detect_suspicious_patterns(self, flow_graph: nx.DiGraph) -> List[Dict]:
        """Detect suspicious patterns in money flow"""
        return []
    
    def _analyze_entities_in_flow(self, flow_graph: nx.DiGraph) -> Dict:
        """Analyze entities involved in money flow"""
        return {"placeholder": "entity_analysis"}
    
    def _analyze_geographic_flow(self, flow_graph: nx.DiGraph) -> Dict:
        """Analyze geographic patterns in money flow"""
        return {"placeholder": "geographic_analysis"}
    
    def _find_complex_cycles(self, account_id: str) -> List[Dict]:
        """Find complex cycles and layering patterns"""
        return []
    
    def _detect_layering_patterns(self, account_id: str) -> List[Dict]:
        """Detect layering patterns"""
        return []
    
    def _assess_layering_risk(self, cycles: List, patterns: List) -> Dict:
        """Assess risk from layering schemes"""
        return {"risk_level": "LOW", "confidence": 0.0}
