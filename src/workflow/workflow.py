from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from src.workflow.workflow_state import WorkflowState
from src.workflow.workflow_memory import sqlite_memory

from src.agents.sql_agent.sql_agent import sql_agent
from src.agents.decision_agent.decision_agent import decision_agent
from src.agents.viz_agent.viz_agent import viz_agent
from src.agents.outros_agent.outros_agent import outros_agent


class Workflow():

    def __init__(self):
        self.memory = sqlite_memory
        self.sql_agent = sql_agent
        self.decision_agent = decision_agent
        self.viz_agent = viz_agent
        self.outros_agent = outros_agent
        graph = StateGraph(WorkflowState)
        graph.add_node("decision_agent", self.__decision_agent)
        graph.add_node("sql_agent", self.__sql_agent)
        graph.add_node("viz_agent", self.__viz_agent)
        graph.add_node("outros_agent", self.__outros_agent)
        graph.set_entry_point("decision_agent")
        graph.add_edge("outros_agent", END)
        graph.add_edge("sql_agent", END)
        graph.add_edge("viz_agent", END)
        graph.add_conditional_edges(
            source="decision_agent",
            path=self.__check_decision,
            path_map={
                "SQL": "sql_agent",
                "VIZ": "viz_agent",
                "OUTROS": "outros_agent"
            }
        )
        self.graph = graph.compile(checkpointer=self.memory)

    def __decision_agent(self, state: WorkflowState):
        
        print("DECISION AGENT")
        print("-"*40)
        print("Current state: \n", state)

        messages = state['messages']
        last_message = messages[-1].content

        print("Last Message: \n", last_message)


        chain_response = self.decision_agent.invoke(last_message)
        chain_response.pretty_print()
        print("-"*40, end='\n\n')

        return {'messages': [chain_response]}

    def __check_decision(self, state: WorkflowState):
        print('DECISION CHECKING')
        print('-'*40)
        print('Current state: \n', state)
        result = state['messages'][-1]
        result.pretty_print()
        print("-"*40, end='\n\n')

        return result.content

    def __sql_agent(self, state: WorkflowState):
        print("SQL AGENT")
        print("-"*40)
        print("Current state: \n", state)

        messages = state['messages']
        human_messages = [message for message in messages if isinstance(message, HumanMessage)]
        last_message = human_messages[-1].content

        print("Last Message: \n", last_message)


        chain_response = self.sql_agent.invoke(last_message)
        chain_response.pretty_print()
        print("-"*40, end='\n\n')

        return {'messages': [chain_response]}

    def __viz_agent(self, state: WorkflowState):
        print("VIZ AGENT")
        print("-"*40)
        print("Current state: \n", state)
        messages = state['messages']

        human_messages = [message for message in messages if isinstance(message, HumanMessage)]

        ai_messages = [message for message in messages if isinstance(message, AIMessage)]
        last_ai_message = ai_messages[-1].content

        last_human_message = human_messages[-1].content

        print("Last AI Message: \n", last_ai_message)
        print("Last Human Message: \n", last_human_message)

        chain_response = self.viz_agent.invoke({"input": last_human_message, "sql_query": last_ai_message})
        
        chain_response.pretty_print()
        print("-"*40, end='\n\n')
    
        return {'messages': [chain_response]}

    def __outros_agent(self, state: WorkflowState):
        messages = state['messages']

        human_messages = [message for message in messages if isinstance(message, HumanMessage)]
        last_human_message = human_messages[-1].content

        message = self.outros_agent.invoke(last_human_message)

        return {'messages': [message]}
