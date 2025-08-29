# from py2neo import Graph, Node, Relationship
# import pandas as pd
# from config import Config

# class GraphDatabase:
#     def __init__(self):
#         try:
#             self.graph = Graph(
#                 Config.NEO4J_URI, 
#                 auth=(Config.NEO4J_USER, Config.NEO4J_PASSWORD)
#             )
#             print("Successfully connected to Neo4j.")
#         except Exception as e:
#             print(f"Failed to connect to Neo4j: {e}")
#             self.graph = None

#     def setup_constraints(self):
#         if not self.graph:
#             print("No graph connection available.")
#             return
#         try:
#             # This constraint ensures that Account nodes are unique based on their ID
#             # and significantly speeds up the MERGE operations.
#             self.graph.run("CREATE CONSTRAINT IF NOT EXISTS FOR (a:Account) REQUIRE a.id IS UNIQUE")
#             print("Unique constraint on Account nodes ensured.")
#         except Exception as e:
#             print(f"Warning: Could not create constraint. It might already exist or there's a DB issue: {e}")

#     def add_transactions_from_df(self, df: pd.DataFrame):
#         if not self.graph:
#             print("No graph connection available.")
#             return
#         print("Merging transactions into the persistent graph...")
#         tx = self.graph.begin()
#         for _, row in df.iterrows():
#             sender_id = str(row['nameOrig'])
#             receiver_id = str(row['nameDest'])
            
#             # MERGE finds an existing node or creates a new one, preventing duplicates.
#             sender_node = Node("Account", id=sender_id)
#             tx.merge(sender_node, "Account", "id")
            
#             receiver_node = Node("Account", id=receiver_id)
#             tx.merge(receiver_node, "Account", "id")
            
#             # CREATE a new relationship for each transaction.
#             # The relationship type is dynamic based on the data (e.g., 'TRANSFER', 'CASH_OUT').
#             transaction_rel = Relationship(
#                 sender_node, 
#                 row['type'], 
#                 receiver_node,
#                 amount=float(row['amount']),
#                 timestamp=int(row['step']),
#                 isFraud=bool(row['isFraud'])
#             )
#             tx.create(transaction_rel)
        
#         tx.commit()
#         print(f"Successfully merged {len(df)} new transactions into the graph.")

#     def get_transaction_graph(self, account_id: str, limit: int = 50):
#         if not self.graph:
#             return {"nodes": [], "links": []}
#         query = """
#         MATCH (a:Account {id: $account_id})-[r]-(b)
#         RETURN a, r, b
#         LIMIT $limit
#         """
#         results = self.graph.run(query, account_id=account_id, limit=limit).data()
        
#         nodes = {}
#         links = []

#         for row in results:
#             node_a_id = row['a']['id']
#             node_b_id = row['b']['id']
#             rel = row['r']
#             rel_type = type(rel).__name__

#             nodes[node_a_id] = {"id": node_a_id, "label": node_a_id}
#             nodes[node_b_id] = {"id": node_b_id, "label": node_b_id}

#             links.append({
#                 "source": rel.start_node['id'],
#                 "target": rel.end_node['id'],
#                 "label": rel_type,
#                 "amount": rel.get('amount', 0)
#             })
            
#         return {"nodes": list(nodes.values()), "links": links}

#     def get_account_history(self, account_id: str, limit: int = 100):
#         """Fetches all incoming and outgoing transactions for a given account."""
#         if not self.graph:
#             return None
#         query = """
#         MATCH (a:Account {id: $account_id})-[r]-(b:Account)
#         RETURN a.id as account, type(r) as type, r.amount as amount, b.id as other_party,
#                CASE WHEN startNode(r) = a THEN 'outgoing' ELSE 'incoming' END as direction
#         ORDER BY r.timestamp DESC
#         LIMIT $limit
#         """
#         results = self.graph.run(query, account_id=account_id, limit=limit)
#         return pd.DataFrame(results.data())

#     def find_cycles(self, account_id: str, max_length: int = 4):
#         if not self.graph:
#             return []
#         query = """
#         MATCH p=(a:Account {id: $account_id})-[*1..%d]->(a)
#         RETURN p
#         """ % max_length
#         results = self.graph.run(query, account_id=account_id).data()
#         return [row['p'] for row in results]

# db_provider = GraphDatabase()







# from py2neo import Graph, Node, Relationship
# import pandas as pd
# from config import Config

# class GraphDatabase:
#     def __init__(self):
#         try:
#             self.graph = Graph(
#                 Config.NEO4J_URI, 
#                 auth=(Config.NEO4J_USER, Config.NEO4J_PASSWORD)
#             )
#             print("Successfully connected to Neo4j.")
#         except Exception as e:
#             print(f"Failed to connect to Neo4j: {e}")
#             self.graph = None

#     def setup_constraints(self):
#         if not self.graph:
#             print("No graph connection available.")
#             return
#         try:
#             self.graph.run("CREATE CONSTRAINT IF NOT EXISTS FOR (a:Account) REQUIRE a.id IS UNIQUE")
#             print("Unique constraint on Account nodes ensured.")
#         except Exception as e:
#             print(f"Warning: Could not create constraint. It might already exist or there's a DB issue: {e}")

#     def add_transactions_from_df(self, df: pd.DataFrame):
#         if not self.graph:
#             print("No graph connection available.")
#             return
#         print("Merging transactions into the persistent graph...")
#         tx = self.graph.begin()
#         for _, row in df.iterrows():
#             sender_id = str(row['nameOrig'])
#             receiver_id = str(row['nameDest'])
            
#             sender_node = Node("Account", id=sender_id)
#             tx.merge(sender_node, "Account", "id")
            
#             receiver_node = Node("Account", id=receiver_id)
#             tx.merge(receiver_node, "Account", "id")
            
#             transaction_rel = Relationship(
#                 sender_node, 
#                 row['type'], 
#                 receiver_node,
#                 amount=float(row['amount']),
#                 timestamp=int(row['step']),
#                 isFraud=bool(row['isFraud'])
#             )
#             tx.create(transaction_rel)
        
#         tx.commit()
#         print(f"Successfully merged {len(df)} new transactions into the graph.")

#     def get_transaction_graph(self, account_id: str, limit: int = 50):
#         if not self.graph:
#             return {"nodes": [], "links": []}
#         query = """
#         MATCH (a:Account {id: $account_id})-[r]-(b)
#         RETURN a, r, b
#         LIMIT $limit
#         """
#         results = self.graph.run(query, account_id=account_id, limit=limit).data()
        
#         nodes = {}
#         links = []

#         for row in results:
#             node_a_id = row['a']['id']
#             node_b_id = row['b']['id']
#             rel = row['r']
#             rel_type = type(rel).__name__

#             nodes[node_a_id] = {"id": node_a_id, "label": node_a_id}
#             nodes[node_b_id] = {"id": node_b_id, "label": node_b_id}

#             links.append({
#                 "source": rel.start_node['id'],
#                 "target": rel.end_node['id'],
#                 "label": rel_type,
#                 "amount": rel.get('amount', 0)
#             })
            
#         return {"nodes": list(nodes.values()), "links": links}

#     def get_account_history(self, account_id: str, limit: int = 100):
#         """Fetches all incoming and outgoing transactions for a given account."""
#         if not self.graph:
#             return None
#         query = """
#         MATCH (a:Account {id: $account_id})-[r]-(b:Account)
#         RETURN a.id as account, type(r) as type, r.amount as amount, b.id as other_party,
#                CASE WHEN startNode(r) = a THEN 'outgoing' ELSE 'incoming' END as direction
#         ORDER BY r.timestamp DESC
#         LIMIT $limit
#         """
#         results = self.graph.run(query, account_id=account_id, limit=limit)
#         return pd.DataFrame(results.data())

#     # --- UPDATED FUNCTION ---
#     def find_all_cycles(self, max_length: int = 5):
#         """Finds all circular transaction paths in the entire graph."""
#         if not self.graph: return []
#         query = f"""
#         MATCH p=(a:Account)-[*3..{max_length}]->(a)
#         UNWIND nodes(p) as node
#         RETURN COLLECT(DISTINCT node.id) as nodes_in_cycles
#         """
#         results = self.graph.run(query).data()
#         if results and results[0]['nodes_in_cycles']:
#             return results[0]['nodes_in_cycles']
#         return []

#     # --- NEW FUNCTION ---
#     def find_high_risk_nodes(self):
#         """Finds all nodes involved in transactions marked as fraudulent."""
#         if not self.graph: return []
#         query = """
#         MATCH (a:Account)-[r]->(b:Account)
#         WHERE r.isFraud = true
#         WITH COLLECT(DISTINCT a.id) + COLLECT(DISTINCT b.id) as risky_nodes
#         RETURN risky_nodes
#         """
#         results = self.graph.run(query).data()
#         # The result is a list of lists, so we flatten it and get unique values
#         if results and results[0]['risky_nodes']:
#             return list(set(results[0]['risky_nodes']))
#         return []

# db_provider = GraphDatabase()










# from py2neo import Graph, Node, Relationship
# import pandas as pd
# from config import Config

# class GraphDatabase:
#     def __init__(self):
#         try:
#             self.graph = Graph(
#                 Config.NEO4J_URI, 
#                 auth=(Config.NEO4J_USER, Config.NEO4J_PASSWORD)
#             )
#             print("Successfully connected to Neo4j.")
#         except Exception as e:
#             print(f"Failed to connect to Neo4j: {e}")
#             self.graph = None

#     def setup_constraints(self):
#         if not self.graph:
#             print("No graph connection available.")
#             return
#         try:
#             self.graph.run("CREATE CONSTRAINT IF NOT EXISTS FOR (a:Account) REQUIRE a.id IS UNIQUE")
#             print("Unique constraint on Account nodes ensured.")
#         except Exception as e:
#             print(f"Warning: Could not create constraint. It might already exist or there's a DB issue: {e}")

#     def add_transactions_from_df(self, df: pd.DataFrame):
#         if not self.graph:
#             print("No graph connection available.")
#             return
#         print("Merging transactions into the persistent graph...")
#         tx = self.graph.begin()
#         for _, row in df.iterrows():
#             sender_id = str(row['nameOrig'])
#             receiver_id = str(row['nameDest'])
            
#             sender_node = Node("Account", id=sender_id)
#             tx.merge(sender_node, "Account", "id")
            
#             receiver_node = Node("Account", id=receiver_id)
#             tx.merge(receiver_node, "Account", "id")
            
#             transaction_rel = Relationship(
#                 sender_node, 
#                 row['type'], 
#                 receiver_node,
#                 amount=float(row['amount']),
#                 timestamp=int(row['step']),
#                 isFraud=bool(row['isFraud'])
#             )
#             tx.create(transaction_rel)
        
#         tx.commit()
#         print(f"Successfully merged {len(df)} new transactions into the graph.")

#     def get_transaction_graph(self, account_id: str, limit: int = 50):
#         if not self.graph:
#             return {"nodes": [], "links": []}
#         # --- CORRECTED QUERY ---
#         # This query now finds the account and then matches any relationships
#         # connected to it, regardless of direction.
#         query = """
#         MATCH (a:Account {id: $account_id})
#         OPTIONAL MATCH (a)-[r]-(b)
#         RETURN a, r, b
#         LIMIT $limit
#         """
#         results = self.graph.run(query, account_id=account_id, limit=limit).data()
        
#         nodes, links = {}, []
        
#         # Handle case where the node exists but has no transactions
#         if not results or results[0]['r'] is None:
#             if self.graph.nodes.match("Account", id=account_id).first():
#                  nodes[account_id] = {"id": account_id, "label": account_id}
#             return {"nodes": list(nodes.values()), "links": links}

#         for row in results:
#             nodes[row['a']['id']] = {"id": row['a']['id'], "label": row['a']['id']}
#             nodes[row['b']['id']] = {"id": row['b']['id'], "label": row['b']['id']}
#             links.append({"source": row['r'].start_node['id'], "target": row['r'].end_node['id'],
#                           "label": type(row['r']).__name__, "amount": row['r'].get('amount', 0)})
#         return {"nodes": list(nodes.values()), "links": links}

#     def get_account_history(self, account_id: str, limit: int = 100):
#         """Fetches all incoming and outgoing transactions for a given account."""
#         if not self.graph:
#             return None
#         query = """
#         MATCH (a:Account {id: $account_id})-[r]-(b:Account)
#         RETURN a.id as account, type(r) as type, r.amount as amount, b.id as other_party,
#                CASE WHEN startNode(r) = a THEN 'outgoing' ELSE 'incoming' END as direction
#         ORDER BY r.timestamp DESC
#         LIMIT $limit
#         """
#         results = self.graph.run(query, account_id=account_id, limit=limit)
#         return pd.DataFrame(results.data())

#     # --- UPDATED FUNCTION ---
#     def find_all_cycles(self, max_length: int = 5):
#         """Finds all circular transaction paths in the entire graph."""
#         if not self.graph: return []
#         query = f"""
#         MATCH p=(a:Account)-[*3..{max_length}]->(a)
#         UNWIND nodes(p) as node
#         RETURN COLLECT(DISTINCT node.id) as nodes_in_cycles
#         """
#         results = self.graph.run(query).data()
#         if results and results[0]['nodes_in_cycles']:
#             return results[0]['nodes_in_cycles']
#         return []

#     # --- NEW FUNCTION ---
#     def find_high_risk_nodes(self):
#         """Finds all nodes involved in transactions marked as fraudulent."""
#         if not self.graph: return []
#         query = """
#         MATCH (a:Account)-[r]->(b:Account)
#         WHERE r.isFraud = true
#         WITH COLLECT(DISTINCT a.id) + COLLECT(DISTINCT b.id) as risky_nodes
#         RETURN risky_nodes
#         """
#         results = self.graph.run(query).data()
#         # The result is a list of lists, so we flatten it and get unique values
#         if results and results[0]['risky_nodes']:
#             return list(set(results[0]['risky_nodes']))
#         return []

# db_provider = GraphDatabase()



from py2neo import Graph, Node, Relationship
import pandas as pd
from config import Config

class GraphDatabase:
    def __init__(self):
        try:
            self.graph = Graph(
                Config.NEO4J_URI, 
                auth=(Config.NEO4J_USER, Config.NEO4J_PASSWORD)
            )
            print("Successfully connected to Neo4j.")
        except Exception as e:
            print(f"Failed to connect to Neo4j: {e}")
            self.graph = None

    def setup_constraints(self):
        if not self.graph:
            print("No graph connection available.")
            return
        try:
            self.graph.run("CREATE CONSTRAINT IF NOT EXISTS FOR (a:Account) REQUIRE a.id IS UNIQUE")
            print("Unique constraint on Account nodes ensured.")
        except Exception as e:
            print(f"Warning: Could not create constraint. It might already exist or there's a DB issue: {e}")

    def add_transactions_from_df(self, df: pd.DataFrame):
        if not self.graph:
            print("No graph connection available.")
            return
        print("Merging transactions into the persistent graph...")
        tx = self.graph.begin()
        for _, row in df.iterrows():
            sender_id = str(row['nameOrig'])
            receiver_id = str(row['nameDest'])
            
            sender_node = Node("Account", id=sender_id)
            tx.merge(sender_node, "Account", "id")
            
            receiver_node = Node("Account", id=receiver_id)
            tx.merge(receiver_node, "Account", "id")
            
            transaction_rel = Relationship(
                sender_node, 
                row['type'], 
                receiver_node,
                amount=float(row['amount']),
                timestamp=int(row['step']),
                isFraud=bool(row['isFraud'])
            )
            tx.create(transaction_rel)
        
        tx.commit()
        print(f"Successfully merged {len(df)} new transactions into the graph.")

    def get_transaction_graph(self, account_id: str, limit: int = 50):
        if not self.graph:
            return {"nodes": [], "links": []}
        # --- CORRECTED QUERY ---
        # This query now finds the account and then matches any relationships
        # connected to it, regardless of direction.
        query = """
        MATCH (a:Account {id: $account_id})
        OPTIONAL MATCH (a)-[r]-(b)
        RETURN a, r, b
        LIMIT $limit
        """
        results = self.graph.run(query, account_id=account_id, limit=limit).data()
        
        nodes, links = {}, []
        
        # Handle case where the node exists but has no transactions
        if not results or results[0]['r'] is None:
            if self.graph.nodes.match("Account", id=account_id).first():
                 nodes[account_id] = {"id": account_id, "label": account_id}
            return {"nodes": list(nodes.values()), "links": links}

        for row in results:
            nodes[row['a']['id']] = {"id": row['a']['id'], "label": row['a']['id']}
            nodes[row['b']['id']] = {"id": row['b']['id'], "label": row['b']['id']}
            links.append({"source": row['r'].start_node['id'], "target": row['r'].end_node['id'],
                          "label": type(row['r']).__name__, "amount": row['r'].get('amount', 0)})
        return {"nodes": list(nodes.values()), "links": links}

    def get_account_history(self, account_id: str, limit: int = 100):
        """Fetches all incoming and outgoing transactions for a given account."""
        if not self.graph:
            return None
        query = """
        MATCH (a:Account {id: $account_id})-[r]-(b:Account)
        RETURN a.id as account, type(r) as type, r.amount as amount, b.id as other_party,
               CASE WHEN startNode(r) = a THEN 'outgoing' ELSE 'incoming' END as direction
        ORDER BY r.timestamp DESC
        LIMIT $limit
        """
        results = self.graph.run(query, account_id=account_id, limit=limit)
        return pd.DataFrame(results.data())

    # --- EXISTING ANALYSIS FUNCTIONS ---
    def find_all_cycles(self, max_length: int = 5):
        """Finds all circular transaction paths in the entire graph."""
        if not self.graph: return []
        query = f"""
        MATCH p=(a:Account)-[*3..{max_length}]->(a)
        UNWIND nodes(p) as node
        RETURN COLLECT(DISTINCT node.id) as nodes_in_cycles
        """
        results = self.graph.run(query).data()
        if results and results[0]['nodes_in_cycles']:
            return results[0]['nodes_in_cycles']
        return []

    def find_high_risk_nodes(self):
        """Finds all nodes involved in transactions marked as fraudulent."""
        if not self.graph: return []
        query = """
        MATCH (a:Account)-[r]->(b:Account)
        WHERE r.isFraud = true
        WITH COLLECT(DISTINCT a.id) + COLLECT(DISTINCT b.id) as risky_nodes
        RETURN risky_nodes
        """
        results = self.graph.run(query).data()
        # The result is a list of lists, so we flatten it and get unique values
        if results and results[0]['risky_nodes']:
            return list(set(results[0]['risky_nodes']))
        return []

    # --- NEW: MISSING METHODS FOR NAVIGATION ENDPOINTS ---
    def get_total_accounts(self):
        """Returns total number of accounts in the database."""
        if not self.graph:
            return 0
        try:
            result = self.graph.run("MATCH (a:Account) RETURN COUNT(a) as total").data()
            return result[0]['total'] if result else 0
        except Exception as e:
            print(f"Error getting total accounts: {e}")
            return 0

    def get_total_transactions(self):
        """Returns total number of transactions (relationships) in the database."""
        if not self.graph:
            return 0
        try:
            result = self.graph.run("MATCH ()-[r]->() RETURN COUNT(r) as total").data()
            return result[0]['total'] if result else 0
        except Exception as e:
            print(f"Error getting total transactions: {e}")
            return 0

    def get_all_account_ids(self, limit: int = 100):
        """Returns a list of all account IDs in the database."""
        if not self.graph:
            return []
        try:
            query = "MATCH (a:Account) RETURN a.id as account_id LIMIT $limit"
            results = self.graph.run(query, limit=limit).data()
            return [row['account_id'] for row in results]
        except Exception as e:
            print(f"Error getting account IDs: {e}")
            return []

    def get_transaction_path(self, account_id: str, max_depth: int = 5):
        """Gets transaction path/trace for an account (for trace investigation)."""
        if not self.graph:
            return []
        try:
            query = """
            MATCH path = (start:Account {id: $account_id})-[r*1..$max_depth]->(end:Account)
            RETURN path
            ORDER BY length(path) DESC
            LIMIT 10
            """
            results = self.graph.run(query, account_id=account_id, max_depth=max_depth).data()
            
            traces = []
            for row in results:
                path = row['path']
                trace = []
                for i, rel in enumerate(path.relationships):
                    trace.append({
                        "step": i + 1,
                        "from": rel.start_node['id'],
                        "to": rel.end_node['id'],
                        "amount": rel.get('amount', 0),
                        "type": type(rel).__name__,
                        "timestamp": rel.get('timestamp', 0)
                    })
                traces.append(trace)
            return traces
        except Exception as e:
            print(f"Error getting transaction path: {e}")
            return []

    # --- ENHANCED HIGH-RISK NODES WITH SCORES ---
    def find_high_risk_nodes_with_scores(self):
        """Enhanced version that returns nodes with calculated risk scores."""
        if not self.graph: return []
        try:
            query = """
            MATCH (a:Account)-[r]-(b:Account)
            WITH a, 
                 COUNT(r) as total_transactions,
                 SUM(CASE WHEN r.isFraud = true THEN 1 ELSE 0 END) as fraud_count,
                 SUM(r.amount) as total_amount
            WHERE fraud_count > 0
            RETURN a.id as account_id, 
                   fraud_count,
                   total_transactions,
                   total_amount,
                   (fraud_count * 1.0 / total_transactions) as risk_score
            ORDER BY risk_score DESC, fraud_count DESC
            LIMIT 50
            """
            results = self.graph.run(query).data()
            return [{"account_id": row['account_id'], "risk_score": row['risk_score'], 
                    "fraud_count": row['fraud_count'], "total_transactions": row['total_transactions']} 
                   for row in results]
        except Exception as e:
            print(f"Error finding high-risk nodes with scores: {e}")
            return []

db_provider = GraphDatabase()