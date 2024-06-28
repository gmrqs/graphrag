from src.agents.viz_agent.model_chain import model_chain
from src.agents.viz_agent.chat_prompt_chain import chat_prompt_chain

viz_agent = (
        chat_prompt_chain
        .pipe(model_chain)
)
