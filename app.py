from langchain_core.messages import HumanMessage
import streamlit as st
from uuid import uuid4

from src.workflow.workflow import Workflow
from src.query_engine import QueryEngine

st.title("Domain Guru 🔮")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    session_id = str(uuid4())
    st.session_state["session_id"] = session_id
    workflow = Workflow()
    st.session_state["workflow"] = workflow
    config={"configurable": {"thread_id": st.session_state["session_id"]}}
    st.session_state["workflow_config"] = config
else:
    session_id = st.session_state["session_id"]
    st.info(f"Session ID: {session_id}")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_prompt := st.chat_input("What is up?"):

    # Display user message in chat message container
    st.chat_message("user").markdown(user_prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    human_prompt = HumanMessage(content=user_prompt)

    ai_response = st.session_state['workflow'].graph.invoke({"messages": [human_prompt]}, config=st.session_state['workflow_config'])

    query_engine = QueryEngine()
    
    response_df = query_engine.query(query=ai_response['messages'][-1].content.replace(';',''))
    st.dataframe(response_df)
    with st.expander("📋 veja o SQL"):
        st.code(body=ai_response['messages'][-1].content, language='sql')
        
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": ai_response['messages'][-1].content})

with st.sidebar:
    st.write("Session ID: \n", st.session_state['session_id'])
    st.write("messages: \n", st.session_state['messages'])