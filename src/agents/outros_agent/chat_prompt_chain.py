from langchain.prompts import ChatPromptTemplate

system_prompt = """
Você é um assistente amigável que
deve responder o questionamento de negócios
ou dados.

Seja claro em suas respostas e 
em seu raciocício.

"""

user_prompt = """
{input}
"""

chat_prompt_chain = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("user", user_prompt)
    ]
)
