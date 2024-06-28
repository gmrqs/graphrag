from langchain_community.graphs import Neo4jGraph
from src.graph_vector_config import GraphVectorConfig

class GraphQueryEngine():

    def __init__(self, config: GraphVectorConfig = GraphVectorConfig):
        self.__config = config

    def get_graph_engine(self) -> Neo4jGraph:

        graph_engine = Neo4jGraph(
            url=self.__config.NEO4J_URL,
            username=self.__config.NEO4J_USERNAME,
            password=self.__config.NEO4J_PASSWORD,
            database=self.__config.NEO4J_DATABASE
        )

        return graph_engine
