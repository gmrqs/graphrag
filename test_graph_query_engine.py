from src.utils.graph_query_engine import GraphQueryEngine

graph_engine = GraphQueryEngine().get_graph_engine()

query_results = graph_engine.query(query="MATCH (t) RETURN t")

print(query_results)