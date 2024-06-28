from langchain_community.vectorstores import Neo4jVector
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_openai.embeddings import OpenAIEmbeddings
from src.utils.graph_vector_config import GraphVectorConfig


class GraphVectorRetriever():

    def __init__(self, config: GraphVectorConfig = GraphVectorConfig):
        self.__config = config
        self.__retriever = self.__build_retriever()

    def get_retriever(self):
        return self.__retriever

    def __build_retriever(self) -> VectorStoreRetriever:
        retriever = Neo4jVector.from_existing_graph(
            embedding=OpenAIEmbeddings(),
            url=self.__config.NEO4J_URL,
            username=self.__config.NEO4J_USERNAME,
            password=self.__config.NEO4J_PASSWORD,
            database=self.__config.NEO4J_DATABASE,
            index_name="column_embeddings",
            node_label="Column",
            text_node_properties=["column_description"],
            embedding_node_property="text_embeddings"
        ).as_retriever()

        return retriever
