>>>>>>> 878aa4807e99ba5a524b32f89c231a7c1196f533
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
<<<<<<< HEAD
=======
            # This constraint ensures that Account nodes are unique based on their ID
            # and significantly speeds up the MERGE operations.
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
            
=======
            # MERGE finds an existing node or creates a new one, preventing duplicates.
>>>>>>> 878aa4807e99ba5a524b32f89c231a7c1196f533
            sender_node = Node("Account", id=sender_id)
            tx.merge(sender_node, "Account", "id")
            
            receiver_node = Node("Account", id=receiver_id)
            tx.merge(receiver_node, "Account", "id")
            
<<<<<<< HEAD
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
        query = """
        MATCH (a:Account {id: $account_id})-[r]-(b)
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

    def find_cycles(self, account_id: str, max_length: int = 4):
        if not self.graph:
            return []
        query = """
        MATCH p=(a:Account {id: $account_id})-[*1..%d]->(a)
        RETURN p
        """ % max_length
        results = self.graph.run(query, account_id=account_id).data()
        return [row['p'] for row in results]

db_provider = GraphDatabase()