from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel


class SqlMessage(BaseModel):
    content: str

output_parser_chain = StrOutputParser()

def output_parser(input: str)-> SqlMessage:
    return SqlMessage(content=input)