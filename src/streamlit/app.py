import streamlit as st
import uuid

st.title("Domain Guru 🔮")

if "messages" not in st.session_state:
    st.session_state.messages = []

if 'session_id' not in st.session_state:
    session_id = str(uuid.uuid4())
    st.session_state['session_id'] = session_id
else:
    session_id = st.session_state['session_id']
    st.info(f"Session ID: {session_id}")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_prompt := st.chat_input("What is up?"):

    # Display user message in chat message container
    st.chat_message("user").markdown(user_prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    response = f"Echo: {prompt}"
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})