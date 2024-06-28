from src.agents.decision_agent.decision_agent import decision_agent

response = decision_agent.invoke("Quem foi Agostinho Carrara?")

print(response, response=="OUTROS")

assert response == 'OUTROS'



response = decision_agent.invoke("Quais os principais categorias de pedidos?")

print(response, response=='SQL')

assert response == 'SQL'


response = decision_agent.invoke("Mostre-me em um gráfico de barras as vendas do ano passado por mês?")

print(response, response=='VIZ')

assert response == 'VIZ'
