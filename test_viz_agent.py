from src.agents.viz_agent.viz_agent import viz_agent

response = viz_agent.invoke({"input": "Mostre em um gráfico de pizza quantos produtos foram vendidos por categoria?", "sql_query": "select * from tb_banana"})


print(response.content)
