from src.agents.sql_agent.sql_agent import sql_agent
from langchain_core.messages import HumanMessage


prompt = "Qual categoria de produto que mais vendeu em 2018?"

response = sql_agent.invoke(input=prompt)

print(response)