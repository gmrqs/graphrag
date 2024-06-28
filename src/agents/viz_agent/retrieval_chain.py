from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from src.agents.sql_agent.sql_agent import sql_agent

retrieval_chain = RunnableParallel(
    {
        "sql_query": sql_agent,
        "input": RunnablePassthrough()
    }
)
