from src.utils.graph_query_engine import GraphQueryEngine
import json

def read_metadata(file_path: str) -> dict:

    with open(file_path, encoding='utf-8') as file:
        metadata = json.load(file)

    return metadata


def wipe_graph_database() -> None:

    graph_engine = GraphQueryEngine().get_graph_engine()

    graph_engine.query(query="MATCH (n) DETACH DELETE n")
    graph_engine.query(query="CALL apoc.schema.assert({},{},true) YIELD label, key RETURN *")
    graph_engine.refresh_schema()


def create_constraints() -> None:

    graph_engine = GraphQueryEngine().get_graph_engine()

    table_constraint = """
    CREATE CONSTRAINT table_uniqueness_rule IF NOT EXISTS 
        FOR (tb:Table) REQUIRE tb.table_full_name IS UNIQUE
    """

    graph_engine.query(query=table_constraint)

    column_constraint = """
    CREATE CONSTRAINT column_uniqueness_rule IF NOT EXISTS 
        FOR (col:Column) REQUIRE col.column_name IS UNIQUE
    """

    graph_engine.query(query=column_constraint)

    database_constraint = """
    CREATE CONSTRAINT database_uniqueness_rule IF NOT EXISTS
        FOR (db:Database) REQUIRE db.database_name IS UNIQUE
    """

    graph_engine.query(query=database_constraint)

def create_table_entities(metadata: dict) -> None:

    graph_engine = GraphQueryEngine().get_graph_engine()

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

        graph_engine.query(query=query_string, params=params)

def create_database_entities(metadata: dict) -> None:

    graph_engine = GraphQueryEngine().get_graph_engine()

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

            graph_engine.query(query=query_string, params=params)


def create_column_entities(metadata: dict) -> None:

    graph_engine = GraphQueryEngine().get_graph_engine()

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

            graph_engine.query(query=query_string, params=params)


def create_contains_relationship() -> None:

    graph_engine = GraphQueryEngine().get_graph_engine()

    query_string = """
        MATCH (tb:Table)
        MATCH (db:Database)
        WHERE tb.table_name in db.database_tables
        CREATE (db)-[:CONTAINS]->(tb)
    """

    graph_engine.query(query=query_string)


def create_has_column_relationship() -> None:

    graph_engine = GraphQueryEngine().get_graph_engine()

    query_string = """
        MATCH (tb:Table)
        MATCH (col:Column)
        WHERE tb.table_name in col.located_at
        CREATE (tb)-[:HAS_COLUMN]->(col)
    """

    graph_engine.query(query=query_string)


def create_is_primary_key_relationship() -> None:

    graph_engine = GraphQueryEngine().get_graph_engine()

    query_string = """
        MATCH (tb:Table)
        MATCH (col:Column) WHERE col.column_name in tb.table_primary_key
        MERGE (col)-[pk:IS_PRIMARY_KEY]->(tb)
    """

    graph_engine.query(query=query_string)


def create_is_primary_key_property() -> None:

    graph_engine = GraphQueryEngine().get_graph_engine()

    query_string = """
    MATCH (tb:Table)
    MATCH (col:Column) WHERE col.column_name in tb.table_primary_key
    SET col.is_primary_key_at = col.is_primary_key_at + tb.table_name
    """

    graph_engine.query(query=query_string)


def create_is_foreign_key_property()->None:

    graph_engine = GraphQueryEngine().get_graph_engine()

    query_string = """
    MATCH (tb:Table)
    MATCH (col:Column)
    WHERE (col)-[:IS_PRIMARY_KEY]->(tb)
    SET col.is_foreign_key_at = apoc.coll.disjunction(col.located_at, [tb.table_name])
    """

    graph_engine.query(query=query_string)


def create_is_foreign_key_relationship() -> None:

    graph_engine = GraphQueryEngine().get_graph_engine()

    query_string = """
        MATCH (tb:Table)
        MATCH (col:Column) WHERE tb.table_name in col.is_foreign_key_at
        MERGE (col)-[:IS_FOREIGN_KEY]->(tb)
    """

    graph_engine.query(query=query_string)


def create_vector_indexes() -> None:

    graph_engine = GraphQueryEngine().get_graph_engine()

    query_string = """
            CREATE VECTOR INDEX `database_embeddings` IF NOT EXISTS
            FOR (db:Database) ON (db.text_embeddings) 
            OPTIONS { indexConfig: {
                `vector.dimensions`: 1536,
                `vector.similarity_function`: 'cosine'
                }
            }
    """
    graph_engine.query(query=query_string)


    query_string = """
            CREATE VECTOR INDEX `table_embeddings` IF NOT EXISTS
            FOR (tb:Table) ON (tb.text_embeddings) 
            OPTIONS { indexConfig: {
                `vector.dimensions`: 1536,
                `vector.similarity_function`: 'cosine'
                }
            }
    """
    graph_engine.query(query=query_string)

    query_string = """
            CREATE VECTOR INDEX `columns_embeddings` IF NOT EXISTS
            FOR (col:Column) ON (col.text_embeddings) 
            OPTIONS { indexConfig: {
                `vector.dimensions`: 1536,
                `vector.similarity_function`: 'cosine'
                }
            }
    """
    graph_engine.query(query=query_string)

    graph_engine.refresh_schema()


def build_graph_database() -> None:

    wipe_graph_database()
    metadata = read_metadata(file_path="metadata.json")
    create_constraints()
    create_table_entities(metadata)
    create_database_entities(metadata)
    create_column_entities(metadata)
    create_contains_relationship()
    create_has_column_relationship()
    create_is_primary_key_relationship()
    create_is_primary_key_property()
    create_is_foreign_key_property()
    create_is_foreign_key_relationship()
    create_is_foreign_key_relationship()
    create_vector_indexes()
