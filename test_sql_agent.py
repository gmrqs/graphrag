from src.sql_agent.sql_agent import sql_agent

response = sql_agent.invoke("Qual categoria de produto que mais vendeu em 2018?")

print(response)