from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage

from src.workflow.workflow_state import WorkflowState
from src.workflow.workflow_memory import sqlite_memory

class Workflow():

    def __init__(self, model, system=""):
        self.system = system
        self.memory = sqlite_memory
        graph = StateGraph(WorkflowState)
        graph.add_node("llm", self.__call)
        graph.set_entry_point("llm")
        graph.add_edge("llm", END)
        self.graph = graph.compile(checkpointer=self.memory)
        self.model = model


    def __call(self, state: WorkflowState):
        messages = state['messages']
        if self.system:
            messages = [SystemMessage(content=self.system)] + messages
        message = self.model.invoke(messages)
        return {'messages': [message]}

agent_manager = Workflow(model=model, tools=[], system=prompt)

messages = [HumanMessage(content="ele nasceu e morreu em que ano?")]
config={"configurable": {"thread_id":123}}
result = agent_manager.graph.invoke({"messages": messages}, config=config)