import os
from dotenv import load_dotenv

load_dotenv(override=True)


class GraphVectorConfig():
    NEO4J_URL = os.environ.get("NEO4J_URL")
    NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME")
    NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD")
    NEO4J_DATABASE = os.environ.get("NEO4J_DATABASE", "neo4j")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
