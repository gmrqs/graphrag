from langchain_core.messages import HumanMessage

# from langchain.globals import set_debug
# set_debug(True)

from src.workflow.workflow import Workflow

workflow = Workflow()

messages = [HumanMessage(content="Quem foi Agustinho Carrara?")]
config={"configurable": {"thread_id":1}}

result = workflow.graph.invoke({"messages": messages}, config=config)

print(result['messages'][-1].content)