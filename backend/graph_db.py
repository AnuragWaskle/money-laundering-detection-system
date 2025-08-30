
from py2neo import Graph, Node, Relationship
import pandas as pd
import logging
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

# Create global database provider instance
db_provider = GraphDatabase()