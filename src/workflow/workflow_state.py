import operator
from typing import TypedDict, Annotated
from langchain_core.messages import AnyMessage


class WorkflowState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
