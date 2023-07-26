import gzip
import pandas as pd
from ast import literal_eval


def getdata(filename: str):
    with gzip.open(f"{filename}", "rt", encoding="UTF-8") as zipfile:
        data = [literal_eval(v.strip().replace("|", " ")) for v in zipfile]
    return data


def json_gz_to_csv(filename: str):
    df = pd.DataFrame(getdata(filename))

    df.to_csv(f"{filename.split('.json.gz')[0]}.csv", index=False, escapechar="|")


def json_gz_to_df(filename: str):
    return pd.DataFrame(getdata(filename))
