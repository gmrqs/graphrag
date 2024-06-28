from src.sql_agent.model_chain import model_chain
from src.sql_agent.chat_prompt_chain import chat_prompt_chain
from src.sql_agent.output_parser_chain import output_parser_chain
from src.sql_agent.retriever_chain import retrieval_chain

sql_agent = (
    retrieval_chain
        .pipe(chat_prompt_chain)
        .pipe(model_chain)
        .pipe(output_parser_chain)
)
