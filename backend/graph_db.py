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

    def add_transactions_from_df(self, df: pd.DataFrame):
        if not self.graph:
            print("No graph connection available.")
            return

        tx = self.graph.begin()
        for index, row in df.iterrows():
            sender_id = str(row['nameOrig'])
            receiver_id = str(row['nameDest'])
            
            sender_node = Node("Account", id=sender_id)
            tx.merge(sender_node, "Account", "id")
            
            receiver_node = Node("Account", id=receiver_id)
            tx.merge(receiver_node, "Account", "id")
            
            transaction_rel = Relationship(
                sender_node, 
                "SENT", 
                receiver_node,
                type=row['type'],
                amount=float(row['amount']),
                timestamp=int(row['step']),
                isFraud=bool(row['isFraud']),
                isFlaggedFraud=bool(row['isFlaggedFraud'])
            )
            tx.create(transaction_rel)
        
        tx.commit()
        print(f"Successfully added {len(df)} transactions to the graph.")

    def get_transaction_graph(self, account_id: str, limit: int = 25):
        if not self.graph:
            print("No graph connection available.")
            return {"nodes": [], "links": []}

        query = """
        MATCH (a:Account {id: $account_id})-[r]-(b)
        RETURN a, r, b
        LIMIT $limit
        """
        
        results = self.graph.run(query, account_id=account_id, limit=limit).data()
        
        nodes = set()
        links = []

        for row in results:
            node_a = row['a']
            node_b = row['b']
            rel = row['r']

            nodes.add((node_a['id'], node_a['id']))
            nodes.add((node_b['id'], node_b['id']))

            links.append({
                "source": node_a['id'],
                "target": node_b['id'],
                "label": rel.__class__.__name__,
                "amount": rel.get('amount', 0)
            })
            
        formatted_nodes = [{"id": id, "label": label} for id, label in nodes]
        
        return {"nodes": formatted_nodes, "links": links}

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
