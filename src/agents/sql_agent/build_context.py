from typing import List
from langchain_core.documents import Document
from src.utils.graph_query_engine import GraphQueryEngine

graph_engine = GraphQueryEngine().get_graph_engine()

def build_context(docs: List[Document]) -> List[str]:

    list_of_lists = [doc.metadata['located_at'] for doc in docs]
    flat_list = [item for sublist in list_of_lists for item in sublist]

    relevant_tables_list = list(set(flat_list))

    query_string = """
    MATCH (t:Table)-[:HAS_COLUMN]->(c:Column)
    WHERE t.table_name in $table_list
    WITH t, collect(
        {
            column_name: c.column_name,
            data_type: c.data_type,
            column_description: c.column_description
        }
    ) AS columns
    RETURN {
        database_name: t.database_name,
        table_name: t.table_name,
        table_description: t.table_description,
        table_columns: columns
    } AS table
    """

    relevant_tables = graph_engine.query(
        query=query_string,
        params={"table_list": relevant_tables_list}
    )

    final_context = ""

    for table in relevant_tables:

        context_template = ""

        columns_text = ""
        for column in table['table']['table_columns']:
            columns_text += ''.join([
                column['column_name'],
                ', ',
                column['data_type'],
                ', Descrição: ',
                column['column_description']
            ])
            columns_text += '\n    '
        context_template += f"""
Database: {table['table']['database_name']}
Tabela: {table['table']['table_name']}
Descrição: {table['table']['table_description']}
Colunas:
    {columns_text}
"""
        final_context += context_template

    return final_context
