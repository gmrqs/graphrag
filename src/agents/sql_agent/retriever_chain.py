from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from src.utils.graph_vector_retriever import GraphVectorRetriever
from src.agents.sql_agent.build_context import build_context

retriever = GraphVectorRetriever().get_retriever()

retrieval_chain = RunnableParallel(
    {
        "context": retriever | build_context,
        "input": RunnablePassthrough()
    }
)
