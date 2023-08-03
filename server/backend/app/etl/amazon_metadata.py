import pandas as pd
import datetime
import re
import numpy as np

cols = [
    "asin",
    "also_buy",
    "also_view",
    "brand",
    "category",
    "date",
    "description",
    "details",
    "feature",
    "image",
    "main_cat",
    "price",
    "rank",
    "title",
]


def filter_date(date: str):
    try:
        datetime.datetime.strptime(date, "%B %d, %Y")
    except ValueError:
        return None


def filter_int(string):
    if (string is not None or string != "") and isinstance(string, str):
        numbers = re.findall(r"\d+", string.replace(",", ""))
        return numbers[0] if len(numbers) > 0 else None
    elif isinstance(string, float) or isinstance(string, int):
        return int(string) if not np.isnan(string) else None
    else:
        return None


def filter_price(string: str):
    if len(string) < 20 and string != "":
        found_numbers = ".".join(re.findall(r"\d+", string.replace(",", ""))[:2])
        if found_numbers == "":
            return None
        return round(float(found_numbers))
    else:
        return None


def clean(df: pd.DataFrame):
    df.drop_duplicates(subset=["asin"], inplace=True)
    df.drop(columns=df.columns.difference(cols), inplace=True)
    df.dropna(subset=["asin"], how="any", inplace=True)
    df["details"] = df["details"].apply(lambda x: x if x is not None else "")
    df["date"] = df["date"].apply(filter_date)
    df["rank"] = df["rank"].apply(filter_int).fillna(0).apply(lambda x: int(x))
    df["description"] = (
        df["description"]
        .apply(lambda x: x if x is not None else [""])
        .apply(lambda x: x[0] if len(x) > 0 else "")
    )
    df["price"] = df["price"].apply(filter_price).fillna(0)
    df[["brand", "main_cat", "title"]] = df[["brand", "main_cat", "title"]].apply(
        lambda x: x[:255]
    )
    return df
