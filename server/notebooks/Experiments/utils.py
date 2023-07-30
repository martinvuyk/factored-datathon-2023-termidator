import gzip
import pandas as pd
from ast import literal_eval
import psycopg2
import os


def df_from_sql(query: str):
    host, port, dbname, username, pwd = (
        os.getenv("SQL_HOST"),
        os.getenv("SQL_PORT"),
        os.getenv("SQL_DATABASE"),
        os.getenv("SQL_USER"),
        os.getenv("SQL_PASSWORD"),
    )

    with psycopg2.connect(
        f"host='{host}' port={port} dbname='{dbname}' user={username} password={pwd}"
    ) as conn:
        dat = pd.read_sql_query(query, conn)
    return dat


def getdata(filename: str):
    with gzip.open(f"{filename}", "rt", encoding="UTF-8") as zipfile:
        data = [literal_eval(v.strip().replace("|", " ")) for v in zipfile]
    return data


def json_gz_to_csv(filename: str):
    df = pd.DataFrame(getdata(filename))

    df.to_csv(f"{filename.split('.json.gz')[0]}.csv", index=False, escapechar="|")


def json_gz_to_df(filename: str):
    return pd.DataFrame(getdata(filename))
