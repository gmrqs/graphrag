import os
import json
from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from wipe_graph import wipe_graph

load_dotenv()

NEO4J_URL = os.getenv("NEO4J_CONNECTION_URL")
NEO4J_USERNAME = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def create_graph() -> Neo4jGraph:

    graph = Neo4jGraph(
        url=NEO4J_URL,
        username=NEO4J_USERNAME,
        password=NEO4J_PASSWORD
    )

    return graph


def read_metadata(file_path: str) -> dict:

    with open(file_path, encoding='utf-8') as file:
        metadata = json.load(file)

    return metadata


def create_constraints(graph: Neo4jGraph) -> None:

    table_constraint = """
    CREATE CONSTRAINT table_uniqueness_rule IF NOT EXISTS 
        FOR (tb:Table) REQUIRE tb.table_full_name IS UNIQUE
    """

    graph.query(query=table_constraint)

    column_constraint = """
    CREATE CONSTRAINT column_uniqueness_rule IF NOT EXISTS 
        FOR (col:Column) REQUIRE col.column_name IS UNIQUE
    """

    graph.query(query=column_constraint)

    database_constraint = """
    CREATE CONSTRAINT database_uniqueness_rule IF NOT EXISTS
        FOR (db:Database) REQUIRE db.database_name IS UNIQUE
    """

    graph.query(query=database_constraint)


def create_table_entities(graph: Neo4jGraph, metadata: dict) -> None:

    for table in metadata['table_metadata']:

        params = {
            "table_name": table['table_name'],
            "database_name": table['database_name'],
            "table_full_name": '.'.join([table['database_name'], table['table_name']]),
            "table_logic_name": table['table_logic_name'],
            "table_description": table['table_description'],
            "table_columns": [column['column_name'] for column in table['table_columns']],
            "table_primary_key": table['table_primary_key']
        }

        query_string = """
        CREATE (tb:Table {
            table_name: $table_name,
            table_logic_name: $table_logic_name,
            database_name: $database_name,
            table_full_name: $table_full_name,
            table_description: $table_description,
            table_columns: $table_columns,
            table_primary_key: $table_primary_key
            }
        )
        """

        graph.query(query=query_string, params=params)


def create_database_entities(graph: Neo4jGraph, metadata: dict) -> None:
    
    for database in metadata['database_metadata']:

        for table in metadata['table_metadata']:

            params = {
                "database_name": database['database_name'],
                "database_description": database['database_description'],
                "table_name": table['table_name']
            }

            query_string = """
            MERGE (db:Database {database_name: $database_name})
            ON CREATE SET // On first execution creates the database entity
                db.database_description = $database_description,
                db.database_tables = [$table_name]
            ON MATCH SET // Updates table list in database entity if a database with the same name exists
                db.database_tables = db.database_tables + [$table_name]
            """

            graph.query(query=query_string, params=params)


def create_column_entities(graph: Neo4jGraph, metadata: dict) -> None:

    for table in metadata['table_metadata']:
        for column in table['table_columns']:
            params = {
                "table_name": table['table_name'],
                "column_name": column['column_name'],
                "column_description": column['column_description'],
                "data_type": column['data_type']
            }

            query_string = """
            MATCH (tb:Table) WHERE tb.table_name = $table_name 
            MERGE (col:Column {column_name: $column_name})
            ON CREATE SET
                col.column_description = $column_description,
                col.data_type = $data_type,
                col.located_at = [$table_name],
                col.is_primary_key_at = [],
                col.is_foreign_key_at = []
            ON MATCH SET
                col.located_at = col.located_at + [tb.table_name]
            """

            graph.query(query=query_string, params=params)


def create_contains_relationship(graph: Neo4jGraph) -> None:
    
    query_string = """
        MATCH (tb:Table)
        MATCH (db:Database)
        WHERE tb.table_name in db.database_tables
        CREATE (db)-[:CONTAINS]->(tb)
    """

    graph.query(query=query_string)


def create_has_column_relationship(graph: Neo4jGraph) -> None:
   
    query_string = """ 
        MATCH (tb:Table)
        MATCH (col:Column)
        WHERE tb.table_name in col.located_at
        CREATE (tb)-[:HAS_COLUMN]->(col)
    """

    graph.query(query=query_string)


def create_is_primary_key_relationship(graph: Neo4jGraph) -> None:
    
    query_string = """ 
        MATCH (tb:Table)
        MATCH (col:Column) WHERE col.column_name in tb.table_primary_key
        MERGE (col)-[pk:IS_PRIMARY_KEY]->(tb)
    """

    graph.query(query=query_string)


def create_is_primary_key_property(graph: Neo4jGraph)->None:
    query_string = """ 
    MATCH (tb:Table)
    MATCH (col:Column) WHERE col.column_name in tb.table_primary_key
    SET col.is_primary_key_at = col.is_primary_key_at + tb.table_name
    """

    graph.query(query=query_string)


def create_is_foreign_key_property(graph: Neo4jGraph)->None:
    query_string = """
    MATCH (tb:Table)
    MATCH (col:Column)
    WHERE (col)-[:IS_PRIMARY_KEY]->(tb)
    SET col.is_foreign_key_at = apoc.coll.disjunction(col.located_at, [tb.table_name])
    """

    graph.query(query=query_string)


def create_is_foreign_key_relationship(graph: Neo4jGraph)->None:
    query_string = """ 
        MATCH (tb:Table)
        MATCH (col:Column) WHERE tb.table_name in col.is_foreign_key_at
        MERGE (col)-[:IS_FOREIGN_KEY]->(tb)
    """

    graph.query(query=query_string)


def create_vector_indexes(graph: Neo4jGraph)-> None:

    graph.query("""
            CREATE VECTOR INDEX `database_embeddings` IF NOT EXISTS
            FOR (db:Database) ON (db.text_embeddings) 
            OPTIONS { indexConfig: {
                `vector.dimensions`: 1536,
                `vector.similarity_function`: 'cosine'    
            }}
    """)

    graph.query("""
            CREATE VECTOR INDEX `table_embeddings` IF NOT EXISTS
            FOR (tb:Table) ON (tb.text_embeddings) 
            OPTIONS { indexConfig: {
                `vector.dimensions`: 1536,
                `vector.similarity_function`: 'cosine'    
            }}
    """)

    graph.query("""
            CREATE VECTOR INDEX `columns_embeddings` IF NOT EXISTS
            FOR (col:Column) ON (col.text_embeddings) 
            OPTIONS { indexConfig: {
                `vector.dimensions`: 1536,
                `vector.similarity_function`: 'cosine'    
            }}
    """)


def setup_graph():
    graph = create_graph()
    wipe_graph(graph=graph)
    metadata = read_metadata("metadata.json")
    create_constraints(graph=graph)
    create_table_entities(graph=graph, metadata=metadata)
    create_database_entities(graph=graph, metadata=metadata)
    create_column_entities(graph=graph, metadata=metadata)
    create_contains_relationship(graph=graph)
    create_has_column_relationship(graph=graph)
    create_is_primary_key_relationship(graph=graph)
    create_is_primary_key_property(graph=graph)
    create_is_foreign_key_property(graph=graph)
    create_is_foreign_key_relationship(graph=graph)
    create_is_foreign_key_relationship(graph=graph)

if __name__ == "__main__":
    setup_graph()
