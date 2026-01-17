import psycopg
from psycopg import sql
import pandas as pd
from io import StringIO
import csv
from typing import List, Optional


def copy_dataframe(
    conn: psycopg.Connection,
    df: pd.DataFrame,
    schema: str,
    table: str,
    columns: Optional[List[str]] = None
):
    if df.empty:
        return

    if columns is None:
        columns = list(df.columns)

    buffer = StringIO()
    df[columns].to_csv(
        buffer,
        index=False,
        header=False,
        quoting=csv.QUOTE_MINIMAL,
        na_rep="\\N"
    )
    buffer.seek(0)

    copy_sql = sql.SQL("""
        COPY {schema}.{table} ({cols})
        FROM STDIN
        WITH (FORMAT csv, DELIMITER ',', NULL '\\N')
    """).format(
        schema=sql.Identifier(schema),
        table=sql.Identifier(table),
        cols=sql.SQL(', ').join(map(sql.Identifier, columns))
    )

    with conn.cursor() as cur:
        with cur.copy(copy_sql) as copy:
            copy.write(buffer.read())

def load_data(
    connect_str: str,
    schema: str,
    table: str,
    df: pd.DataFrame,
    columns: Optional[List[str]] = None
):
    if df.empty:
        return

    with psycopg.connect(connect_str) as conn:
        copy_dataframe(
            conn=conn,
            df=df,
            schema=schema,
            table=table,
            columns=columns
        )
        conn.commit()

def get_new_ids_by_temp_table(
    connect_str: str,
    warehouse_schema: str,
    table: str,
    id_col: str,
    id_list: List[str]
) -> List[str]:

    if not id_list:
        return []

    df_temp = pd.DataFrame({id_col: id_list}).astype(str)

    buffer = StringIO()
    df_temp.to_csv(
        buffer,
        index=False,
        header=False,
        quoting=csv.QUOTE_MINIMAL,
        na_rep="\\N"
    )
    buffer.seek(0)

    temp_table = f"tmp_check_{table}"

    with psycopg.connect(connect_str) as conn:
        with conn.cursor() as cur:
            # 1. Create temp table
            cur.execute(sql.SQL("""
                CREATE TEMP TABLE {temp} (
                    {id_col} TEXT
                ) ON COMMIT DROP
            """).format(
                temp=sql.Identifier(temp_table),
                id_col=sql.Identifier(id_col)
            ))

            # 2. COPY into temp table
            copy_sql = sql.SQL("""
                COPY {temp} ({id_col})
                FROM STDIN
                WITH (FORMAT csv, DELIMITER ',', NULL '\\N')
            """).format(
                temp=sql.Identifier(temp_table),
                id_col=sql.Identifier(id_col)
            )

            with cur.copy(copy_sql) as copy:
                copy.write(buffer.read())

            # 3. EXCEPT query
            query = sql.SQL("""
                SELECT {id_col} FROM {temp}
                EXCEPT
                SELECT {id_col}::text FROM {schema}.{target}
            """).format(
                id_col=sql.Identifier(id_col),
                temp=sql.Identifier(temp_table),
                schema=sql.Identifier(warehouse_schema),
                target=sql.Identifier(table)
            )

            cur.execute(query)
            result = [row[0] for row in cur.fetchall()]

        conn.commit()
        return result

        
def read_table(
    connect_str: str,
    schema: str,
    table: str,
    limit: Optional[int] = None
) -> pd.DataFrame:

    query = f"SELECT * FROM {schema}.{table}"
    if limit:
        query += f" LIMIT {limit}"

    with psycopg.connect(connect_str) as conn:
        return pd.read_sql(query, conn)
