from langchain_community.graphs import Neo4jGraph

def wipe_graph(graph: Neo4jGraph) -> None:
    graph.query(query="MATCH (n) DETACH DELETE n")
    graph.query(query="CALL apoc.schema.assert({},{},true) YIELD label, key RETURN *")
    graph.refresh_schema()