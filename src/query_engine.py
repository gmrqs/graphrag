import os
import pandas as pd
from pandas import DataFrame
from sqlalchemy import create_engine


class QueryEngineConfig():
    TRINO_USERNAME = os.environ.get("TRINO_USERNAME", "trino")
    TRINO_PASSWORD = os.environ.get("TRINO_PASSWORD", "")
    TRINO_URL = os.environ.get("TRINO_URL", "localhost:8080")
    TRINO_CATALOG = os.environ.get("TRINO_CATALOG", "hive")


class QueryEngine():

    def __init__(self):
        self.__config = QueryEngineConfig()
        self.__engine = create_engine(
            url="trino://{}:{}@{}/{}".format(
                self.__config.TRINO_USERNAME,
                self.__config.TRINO_PASSWORD,
                self.__config.TRINO_URL,
                self.__config.TRINO_CATALOG
            )
        )
        self.__connection = self.__connect()

    def __connect(self):

        connection = self.__engine.connect()
        return connection

    def query(self, query: str) -> DataFrame:

        result_dataframe = pd.read_sql_query(
            sql=query,
            con=self.__connection
        )

        return result_dataframe


if __name__ == "__main__":

    query_engine = QueryEngine()

    query_string = """
    SELECT
        oi.product_id,
        SUM(oi.price) AS total_vendas
    FROM
        olist.dim_order_items oi
    JOIN
        olist.fact_orders fo ON oi.order_id = fo.order_id
    WHERE
        year(fo.order_purchase_timestamp) = 2018
    GROUP BY
        oi.product_id
    ORDER BY
        total_vendas DESC
    LIMIT 10
    """

    df = query_engine.query(query=query_string)

    print(df.head(20))
