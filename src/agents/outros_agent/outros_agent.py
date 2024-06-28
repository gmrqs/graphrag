from src.agents.outros_agent.model_chain import model_chain
from src.agents.outros_agent.chat_prompt_chain import chat_prompt_chain
from src.agents.outros_agent.output_parser_chain import output_parser_chain

outros_agent = (
        chat_prompt_chain
        .pipe(model_chain)
)
