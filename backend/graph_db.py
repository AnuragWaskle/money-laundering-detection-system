
from py2neo import Graph, Node, Relationship
import pandas as pd
import numpy as np
import logging
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

class GraphDatabase:
    def __init__(self):
        self.graph = None
        self._connect()

    def _connect(self):
        """Establish connection to Neo4j database with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.graph = Graph(
                    Config.NEO4J_URI, 
                    auth=(Config.NEO4J_USER, Config.NEO4J_PASSWORD)
                )
                # Test connection
                self.graph.run("RETURN 1")
                logger.info("Successfully connected to Neo4j")
                return
            except Exception as e:
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    logger.error("Failed to connect to Neo4j after all attempts")
                    self.graph = None

    def is_connected(self):
        """Check if database connection is available"""
        if not self.graph:
            return False
        try:
            self.graph.run("RETURN 1")
            return True
        except:
            return False

    def setup_constraints(self):
        """Setup database constraints and indexes"""
        if not self.graph:
            logger.warning("No graph connection available for constraint setup")
            return
        
        try:
            # Create unique constraint on Account nodes
            self.graph.run(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (a:Account) REQUIRE a.id IS UNIQUE"
            )
            
            # Create indexes for better performance
            self.graph.run(
                "CREATE INDEX IF NOT EXISTS FOR (a:Account) ON (a.id)"
            )
            
            logger.info("Database constraints and indexes setup completed")
        except Exception as e:
            logger.error(f"Failed to setup constraints: {e}")

    def add_transactions_from_df(self, df: pd.DataFrame):
        """Add transactions from DataFrame to the graph"""
        if not self.graph:
            logger.error("No graph connection available")
            raise ConnectionError("Database connection unavailable")
        
        if df.empty:
            logger.warning("Empty DataFrame provided")
            return
        
        logger.info(f"Adding {len(df)} transactions to the graph")
        
        try:
            tx = self.graph.begin()
            
            for _, row in df.iterrows():
                sender_id = str(row['nameOrig'])
                receiver_id = str(row['nameDest'])
                
                # Create or merge account nodes
                sender_node = Node("Account", id=sender_id)
                tx.merge(sender_node, "Account", "id")
                
                receiver_node = Node("Account", id=receiver_id)
                tx.merge(receiver_node, "Account", "id")
                
                # Create transaction relationship
                transaction_rel = Relationship(
                    sender_node, 
                    row['type'],
                    receiver_node,
                    amount=float(row['amount']),
                    timestamp=int(row['step']),
                    isFraud=bool(row.get('isFraud', False))
                )
                tx.create(transaction_rel)
            
            tx.commit()
            logger.info(f"Successfully added {len(df)} transactions to the graph")
            
        except Exception as e:
            logger.error(f"Failed to add transactions: {e}")
            raise

    def get_transaction_graph(self, account_id: str, limit: int = 50):
        """Get transaction graph for a specific account"""
        if not self.graph:
            return {"nodes": [], "links": []}
        
        try:
            query = """
            MATCH (a:Account {id: $account_id})-[r]-(b:Account)
            RETURN a, r, b
            LIMIT $limit
            """
            results = self.graph.run(query, account_id=account_id, limit=limit).data()
            
            nodes = {}
            links = []

            for row in results:
                node_a_id = row['a']['id']
                node_b_id = row['b']['id']
                rel = row['r']
                rel_type = type(rel).__name__

                nodes[node_a_id] = {"id": node_a_id, "label": node_a_id}
                nodes[node_b_id] = {"id": node_b_id, "label": node_b_id}

                links.append({
                    "source": rel.start_node['id'],
                    "target": rel.end_node['id'],
                    "label": rel_type,
                    "amount": rel.get('amount', 0)
                })
                
            return {"nodes": list(nodes.values()), "links": links}
            
        except Exception as e:
            logger.error(f"Error getting transaction graph: {e}")
            return {"nodes": [], "links": []}

    def get_account_history(self, account_id: str, limit: int = 100):
        """Get transaction history for an account"""
        if not self.graph:
            return pd.DataFrame()
        
        try:
            query = """
            MATCH (a:Account {id: $account_id})-[r]-(b:Account)
            RETURN a.id as account, type(r) as type, r.amount as amount, 
                   b.id as other_party, r.timestamp as timestamp,
                   CASE WHEN startNode(r) = a THEN 'outgoing' ELSE 'incoming' END as direction
            ORDER BY r.timestamp DESC
            LIMIT $limit
            """
            results = self.graph.run(query, account_id=account_id, limit=limit)
            return pd.DataFrame(results.data())
            
        except Exception as e:
            logger.error(f"Error getting account history: {e}")
            return pd.DataFrame()

    def find_cycles(self, account_id: str, max_length: int = 4):
        """Find cycles involving a specific account"""
        if not self.graph:
            return []
        
        try:
            query = """
            MATCH p=(a:Account {id: $account_id})-[*1..%d]->(a)
            RETURN p
            LIMIT 100
            """ % max_length
            results = self.graph.run(query, account_id=account_id).data()
            return [row['p'] for row in results]
            
        except Exception as e:
            logger.error(f"Error finding cycles: {e}")
            return []

    def find_all_cycles(self, max_length: int = 4):
        """Find all cycles in the graph"""
        if not self.graph:
            return []
        
        try:
            query = """
            MATCH p=(a:Account)-[*2..%d]->(a)
            RETURN DISTINCT a.id as account_id
            LIMIT 1000
            """ % max_length
            results = self.graph.run(query).data()
            return [{"account_id": row["account_id"]} for row in results]
            
        except Exception as e:
            logger.error(f"Error finding all cycles: {e}")
            return []

    def find_high_risk_nodes(self, min_amount: float = 10000.0):
        """Find accounts with high-risk characteristics"""
        if not self.graph:
            return []
        
        try:
            query = """
            MATCH (a:Account)-[r]->(b:Account)
            WHERE r.amount > $min_amount OR r.isFraud = true
            WITH a, sum(r.amount) as total_amount, count(r) as transaction_count,
                 sum(CASE WHEN r.isFraud THEN 1 ELSE 0 END) as fraud_count
            WHERE total_amount > $min_amount OR fraud_count > 0
            RETURN a.id as account_id, total_amount, transaction_count, fraud_count,
                   (total_amount / 1000000.0 + fraud_count * 0.5) as risk_score
            ORDER BY risk_score DESC
            LIMIT 100
            """
            results = self.graph.run(query, min_amount=min_amount).data()
            return results
            
        except Exception as e:
            logger.error(f"Error finding high-risk nodes: {e}")
            return []

    def get_total_accounts(self):
        """Get total number of accounts"""
        if not self.graph:
            return 0
        
        try:
            result = self.graph.run("MATCH (a:Account) RETURN count(a) as count").data()
            return result[0]["count"] if result else 0
        except Exception as e:
            logger.error(f"Error getting total accounts: {e}")
            return 0

    def get_total_transactions(self):
        """Get total number of transactions"""
        if not self.graph:
            return 0
        
        try:
            result = self.graph.run("MATCH ()-[r]->() RETURN count(r) as count").data()
            return result[0]["count"] if result else 0
        except Exception as e:
            logger.error(f"Error getting total transactions: {e}")
            return 0

    def get_all_account_ids(self, limit: int = 1000):
        """Get list of all account IDs"""
        if not self.graph:
            return []
        
        try:
            query = "MATCH (a:Account) RETURN a.id as account_id LIMIT $limit"
            results = self.graph.run(query, limit=limit).data()
            return [row["account_id"] for row in results]
        except Exception as e:
            logger.error(f"Error getting account IDs: {e}")
            return []

    def get_transaction_path(self, account_id: str, max_depth: int = 5):
        """Get transaction paths from an account"""
        if not self.graph:
            return []
        
        try:
            query = """
            MATCH p=(a:Account {id: $account_id})-[*1..%d]->(b:Account)
            RETURN p
            LIMIT 50
            """ % max_depth
            results = self.graph.run(query, account_id=account_id).data()
            
            paths = []
            for row in results:
                path = row['p']
                path_data = {
                    "nodes": [node['id'] for node in path.nodes],
                    "relationships": [
                        {
                            "type": type(rel).__name__,
                            "amount": rel.get('amount', 0),
                            "timestamp": rel.get('timestamp', 0)
                        }
                        for rel in path.relationships
                    ]
                }
                paths.append(path_data)
            
            return paths
            
        except Exception as e:
            logger.error(f"Error getting transaction path: {e}")
            return []

    def trace_money_flow(self, account_id: str, amount_threshold: float = 10000, max_depth: int = 6):
        """Trace money flow across multiple accounts with enhanced tracking"""
        if not self.graph:
            return {"error": "Database connection unavailable"}
        
        try:
            # Complex query to trace money flows above threshold
            query = """
            MATCH p=(source:Account {id: $account_id})-[r*1..%d]->(destination:Account)
            WHERE ALL(rel in r WHERE rel.amount >= $amount_threshold)
            WITH p, [rel in relationships(p) | rel.amount] as amounts,
                 [rel in relationships(p) | rel.timestamp] as timestamps,
                 length(p) as depth
            WHERE depth >= 2
            RETURN p, amounts, timestamps, depth,
                   reduce(total = 0, amount in amounts | total + amount) as total_amount
            ORDER BY total_amount DESC
            LIMIT 100
            """ % max_depth
            
            results = self.graph.run(query, account_id=account_id, amount_threshold=amount_threshold).data()
            
            flow_paths = []
            for row in results:
                path = row['p']
                flow_paths.append({
                    "path_id": len(flow_paths),
                    "source": account_id,
                    "destination": path.nodes[-1]['id'],
                    "nodes": [node['id'] for node in path.nodes],
                    "amounts": row['amounts'],
                    "timestamps": row['timestamps'],
                    "total_amount": row['total_amount'],
                    "depth": row['depth'],
                    "suspicious_indicators": self._analyze_path_suspicion(row)
                })
            
            return {
                "source_account": account_id,
                "total_paths": len(flow_paths),
                "high_value_paths": flow_paths,
                "analysis": self._analyze_money_flows(flow_paths),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error tracing money flow: {e}")
            return {"error": str(e)}

    def detect_circular_transactions(self, min_amount: float = 5000, max_cycle_length: int = 8):
        """Detect circular money flows that could indicate layering"""
        if not self.graph:
            return []
        
        try:
            query = """
            MATCH p=(a:Account)-[r*2..%d]->(a)
            WHERE ALL(rel in r WHERE rel.amount >= $min_amount)
            WITH p, [rel in relationships(p) | rel.amount] as amounts,
                 [rel in relationships(p) | rel.timestamp] as timestamps
            RETURN p, amounts, timestamps,
                   reduce(total = 0, amount in amounts | total + amount) as total_amount,
                   length(p) as cycle_length
            ORDER BY total_amount DESC
            LIMIT 50
            """ % max_cycle_length
            
            results = self.graph.run(query, min_amount=min_amount).data()
            
            cycles = []
            for row in results:
                path = row['p']
                cycle_analysis = self._analyze_cycle_pattern(row)
                
                cycles.append({
                    "cycle_id": len(cycles),
                    "root_account": path.nodes[0]['id'],
                    "nodes": [node['id'] for node in path.nodes],
                    "amounts": row['amounts'],
                    "timestamps": row['timestamps'],
                    "total_amount": row['total_amount'],
                    "cycle_length": row['cycle_length'],
                    "time_span": max(row['timestamps']) - min(row['timestamps']) if row['timestamps'] else 0,
                    "layering_indicators": cycle_analysis
                })
            
            return cycles
            
        except Exception as e:
            logger.error(f"Error detecting circular transactions: {e}")
            return []

    def find_shell_company_networks(self):
        """Identify potential shell company networks"""
        if not self.graph:
            return []
        
        try:
            query = """
            MATCH (a:Account)-[r1]->(b:Account)-[r2]->(c:Account)
            WHERE a.id <> c.id 
            AND (r1.amount > 50000 OR r2.amount > 50000)
            WITH a, b, c, r1.amount + r2.amount as total_flow,
                 r1.timestamp as first_timestamp, r2.timestamp as second_timestamp
            WHERE abs(second_timestamp - first_timestamp) <= 86400  // Within 24 hours
            AND (a.id CONTAINS 'LLC' OR a.id CONTAINS 'CORP' OR a.id CONTAINS 'HOLDING' OR
                 b.id CONTAINS 'LLC' OR b.id CONTAINS 'CORP' OR b.id CONTAINS 'HOLDING' OR
                 c.id CONTAINS 'LLC' OR c.id CONTAINS 'CORP' OR c.id CONTAINS 'HOLDING')
            RETURN a.id as source, b.id as intermediary, c.id as destination,
                   total_flow, first_timestamp, second_timestamp
            ORDER BY total_flow DESC
            LIMIT 100
            """
            
            results = self.graph.run(query).data()
            
            networks = []
            for row in results:
                networks.append({
                    "network_id": len(networks),
                    "source": row['source'],
                    "intermediary": row['intermediary'],
                    "destination": row['destination'],
                    "total_flow": row['total_flow'],
                    "time_span": row['second_timestamp'] - row['first_timestamp'],
                    "shell_indicators": self._identify_shell_indicators([
                        row['source'], row['intermediary'], row['destination']
                    ])
                })
            
            return networks
            
        except Exception as e:
            logger.error(f"Error finding shell company networks: {e}")
            return []

    def analyze_cash_intensive_patterns(self, min_cash_amount: float = 10000):
        """Analyze cash-in/cash-out patterns that might indicate structuring"""
        if not self.graph:
            return []
        
        try:
            query = """
            MATCH (a:Account)-[r:CASH_OUT|CASH_IN]-(b:Account)
            WHERE r.amount >= $min_cash_amount
            WITH a, type(r) as operation_type, r.amount as amount, r.timestamp as timestamp
            ORDER BY a.id, timestamp
            WITH a, collect({op: operation_type, amount: amount, timestamp: timestamp}) as operations
            WHERE size(operations) >= 5
            RETURN a.id as account_id, operations,
                   reduce(total = 0, op in operations | 
                     total + CASE WHEN op.op = 'CASH_OUT' THEN op.amount ELSE 0 END) as total_cash_out,
                   reduce(total = 0, op in operations | 
                     total + CASE WHEN op.op = 'CASH_IN' THEN op.amount ELSE 0 END) as total_cash_in
            ORDER BY (total_cash_out + total_cash_in) DESC
            LIMIT 50
            """
            
            results = self.graph.run(query, min_cash_amount=min_cash_amount).data()
            
            patterns = []
            for row in results:
                operations = row['operations']
                structuring_analysis = self._analyze_structuring_pattern(operations)
                
                patterns.append({
                    "account_id": row['account_id'],
                    "total_cash_out": row['total_cash_out'],
                    "total_cash_in": row['total_cash_in'],
                    "operation_count": len(operations),
                    "operations": operations,
                    "structuring_indicators": structuring_analysis,
                    "risk_score": self._calculate_cash_pattern_risk(row, structuring_analysis)
                })
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing cash patterns: {e}")
            return []

    def find_offshore_connection_patterns(self):
        """Find patterns involving offshore accounts and jurisdictions"""
        if not self.graph:
            return []
        
        # Define offshore jurisdiction patterns
        offshore_patterns = ['BM', 'KY', 'VI', 'BS', 'PA', 'CH', 'SG', 'HK']
        
        try:
            # Build the pattern matching for offshore accounts
            offshore_condition = " OR ".join([f"a.id STARTS WITH '{pattern}'" for pattern in offshore_patterns])
            
            query = f"""
            MATCH (a:Account)-[r]->(b:Account)
            WHERE ({offshore_condition}) OR 
                  (a.id CONTAINS 'OFFSHORE' OR b.id CONTAINS 'OFFSHORE')
            WITH a, b, r, 
                 CASE WHEN {offshore_condition} THEN 'offshore' ELSE 'domestic' END as source_type,
                 CASE WHEN b.id STARTS WITH 'BM' OR b.id STARTS WITH 'KY' OR b.id STARTS WITH 'VI' 
                      OR b.id CONTAINS 'OFFSHORE' THEN 'offshore' ELSE 'domestic' END as dest_type
            WHERE r.amount > 25000
            RETURN a.id as source, b.id as destination, r.amount as amount, 
                   r.timestamp as timestamp, source_type, dest_type
            ORDER BY r.amount DESC
            LIMIT 100
            """
            
            results = self.graph.run(query).data()
            
            patterns = []
            for row in results:
                patterns.append({
                    "source": row['source'],
                    "destination": row['destination'],
                    "amount": row['amount'],
                    "timestamp": row['timestamp'],
                    "source_type": row['source_type'],
                    "destination_type": row['dest_type'],
                    "pattern_type": self._classify_offshore_pattern(row),
                    "risk_indicators": self._assess_offshore_risk(row)
                })
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error finding offshore patterns: {e}")
            return []

    def calculate_account_centrality_metrics(self, account_id: str):
        """Calculate advanced centrality metrics for risk assessment"""
        if not self.graph:
            return {}
        
        try:
            # Get the account's network neighborhood
            query = """
            MATCH (center:Account {id: $account_id})
            OPTIONAL MATCH (center)-[r1]-(neighbor:Account)
            OPTIONAL MATCH (neighbor)-[r2]-(second_degree:Account)
            WHERE second_degree.id <> center.id
            RETURN center, collect(DISTINCT neighbor) as neighbors, 
                   collect(DISTINCT second_degree) as second_degree_nodes,
                   collect(DISTINCT r1) as direct_relationships,
                   collect(DISTINCT r2) as indirect_relationships
            """
            
            result = self.graph.run(query, account_id=account_id).data()
            
            if not result:
                return {}
            
            data = result[0]
            
            # Calculate metrics
            direct_connections = len(data['neighbors'])
            second_degree_connections = len(data['second_degree_nodes'])
            total_transaction_volume = sum(rel.get('amount', 0) for rel in data['direct_relationships'])
            
            # Calculate transaction velocity
            timestamps = [rel.get('timestamp', 0) for rel in data['direct_relationships']]
            time_span = max(timestamps) - min(timestamps) if len(timestamps) > 1 else 0
            transaction_velocity = len(timestamps) / max(time_span / 86400, 1)  # transactions per day
            
            return {
                "account_id": account_id,
                "direct_connections": direct_connections,
                "second_degree_connections": second_degree_connections,
                "total_transaction_volume": total_transaction_volume,
                "transaction_velocity": transaction_velocity,
                "network_reach": direct_connections + second_degree_connections,
                "centrality_score": self._calculate_centrality_score(
                    direct_connections, second_degree_connections, total_transaction_volume
                )
            }
            
        except Exception as e:
            logger.error(f"Error calculating centrality metrics: {e}")
            return {}

    # Helper methods for analysis
    def _analyze_path_suspicion(self, path_data):
        """Analyze a transaction path for suspicious indicators"""
        indicators = []
        
        amounts = path_data.get('amounts', [])
        timestamps = path_data.get('timestamps', [])
        
        # Check for amount patterns
        if amounts:
            # Rapid value decrease (potential layering)
            if len(amounts) > 2 and amounts[0] > amounts[-1] * 2:
                indicators.append("Rapid value decrease through chain")
            
            # Round amounts (potential structuring)
            round_amounts = sum(1 for amount in amounts if amount % 1000 == 0)
            if round_amounts / len(amounts) > 0.7:
                indicators.append("High percentage of round amounts")
        
        # Check for timing patterns
        if timestamps and len(timestamps) > 1:
            time_diffs = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
            avg_time_diff = sum(time_diffs) / len(time_diffs)
            
            # Very rapid transactions
            if avg_time_diff < 3600:  # Less than 1 hour average
                indicators.append("Rapid sequential transactions")
        
        return indicators

    def _analyze_cycle_pattern(self, cycle_data):
        """Analyze a circular transaction pattern"""
        indicators = []
        
        amounts = cycle_data.get('amounts', [])
        timestamps = cycle_data.get('timestamps', [])
        
        if amounts:
            # Check if amounts decrease through the cycle (fee skimming)
            if amounts[0] > amounts[-1]:
                loss_percentage = (amounts[0] - amounts[-1]) / amounts[0] * 100
                indicators.append(f"Value loss through cycle: {loss_percentage:.1f}%")
            
            # Check for consistent amounts (automated behavior)
            amount_variance = np.var(amounts) if len(amounts) > 1 else 0
            if amount_variance < np.mean(amounts) * 0.1:
                indicators.append("Highly consistent transaction amounts")
        
        if timestamps:
            # Check for regular timing
            if len(timestamps) > 2:
                time_diffs = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
                if np.std(time_diffs) < np.mean(time_diffs) * 0.2:
                    indicators.append("Regular transaction timing pattern")
        
        return indicators

    def _identify_shell_indicators(self, account_ids):
        """Identify shell company indicators in account names"""
        indicators = []
        
        shell_keywords = ['LLC', 'CORP', 'HOLDING', 'INVEST', 'CAPITAL', 'MANAGEMENT', 'SERVICES']
        
        for account_id in account_ids:
            account_upper = account_id.upper()
            matching_keywords = [kw for kw in shell_keywords if kw in account_upper]
            if matching_keywords:
                indicators.append(f"{account_id}: {', '.join(matching_keywords)}")
        
        return indicators

    def _analyze_structuring_pattern(self, operations):
        """Analyze operations for structuring patterns"""
        indicators = []
        
        # Check for amounts just below reporting thresholds
        thresholds = [10000, 5000, 3000]
        for threshold in thresholds:
            near_threshold = sum(1 for op in operations 
                               if threshold * 0.9 <= op['amount'] < threshold)
            if near_threshold >= 3:
                indicators.append(f"{near_threshold} transactions near ${threshold} threshold")
        
        # Check for rapid succession of cash operations
        cash_out_ops = [op for op in operations if op['op'] == 'CASH_OUT']
        if len(cash_out_ops) >= 5:
            timestamps = [op['timestamp'] for op in cash_out_ops]
            if max(timestamps) - min(timestamps) <= 86400 * 7:  # Within a week
                indicators.append("Multiple cash-out operations within short timeframe")
        
        return indicators

    def _calculate_cash_pattern_risk(self, data, structuring_analysis):
        """Calculate risk score for cash transaction patterns"""
        risk_score = 0.0
        
        # High volume risk
        total_volume = data['total_cash_out'] + data['total_cash_in']
        if total_volume > 500000:
            risk_score += 0.3
        
        # High frequency risk
        if data['operation_count'] > 20:
            risk_score += 0.2
        
        # Structuring indicators
        risk_score += len(structuring_analysis) * 0.1
        
        # Imbalance (more out than in, suggesting cash conversion)
        if data['total_cash_out'] > data['total_cash_in'] * 2:
            risk_score += 0.2
        
        return min(risk_score, 1.0)

    def _classify_offshore_pattern(self, pattern_data):
        """Classify the type of offshore transaction pattern"""
        source_type = pattern_data['source_type']
        dest_type = pattern_data['destination_type']
        
        if source_type == 'domestic' and dest_type == 'offshore':
            return 'outbound_offshore'
        elif source_type == 'offshore' and dest_type == 'domestic':
            return 'inbound_offshore'
        elif source_type == 'offshore' and dest_type == 'offshore':
            return 'offshore_to_offshore'
        else:
            return 'domestic_to_domestic'

    def _assess_offshore_risk(self, pattern_data):
        """Assess risk factors for offshore transactions"""
        indicators = []
        
        # High amounts to offshore
        if pattern_data['amount'] > 100000:
            indicators.append("High-value offshore transaction")
        
        # Pattern-based risk
        pattern_type = self._classify_offshore_pattern(pattern_data)
        if pattern_type == 'offshore_to_offshore':
            indicators.append("Offshore-to-offshore movement")
        elif pattern_type == 'outbound_offshore':
            indicators.append("Domestic funds moving offshore")
        
        return indicators

    def _calculate_centrality_score(self, direct_conn, second_degree_conn, volume):
        """Calculate a centrality-based risk score"""
        # Normalize components
        connection_score = min((direct_conn + second_degree_conn * 0.5) / 100, 1.0)
        volume_score = min(volume / 10000000, 1.0)  # Normalize to 10M
        
        return (connection_score * 0.6 + volume_score * 0.4)

# Create global database provider instance
db_provider = GraphDatabase()