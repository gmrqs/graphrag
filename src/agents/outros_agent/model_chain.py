from langchain_openai import ChatOpenAI

model_chain = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.0
)
