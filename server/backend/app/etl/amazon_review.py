import pandas as pd
import datetime
import numpy as np
from app.etl.amazon_metadata import filter_int

cols = [
    "asin",
    "overall",
    "reviewText",
    "reviewerID",
    "reviewerName",
    "summary",
    "unixReviewTime",
    "verified",
    "style",
    "vote",
    "image",
]

must = ["asin", "overall", "reviewerID", "reviewText", "reviewerName"]


def force_try(x, *fns):
    try:
        return any(fn(x) for fn in fns)
    except:
        return True


def im_sick_of_this_dataset(x):
    is_nan_float = lambda x: np.isnan(x) or isinstance(x, float) or x == 0
    is_nan_string = lambda x: x.lower() == "nan" or x.lower() == "null"
    is_inf_string = (
        lambda x: x.lower() == "inf"
        or x.lower() == "-inf"
        or x.lower() == "infinity"
        or x.lower() == "-infinity"
    )
    just_to_ensure = lambda x: x is None
    return not force_try(x, is_nan_string, is_nan_float, just_to_ensure, is_inf_string)


def clean(df: pd.DataFrame):
    df.drop_duplicates(subset=["asin", "reviewerID"], inplace=True)
    df.drop(columns=df.columns.difference(cols), inplace=True)

    is_filth = im_sick_of_this_dataset
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(subset=must, how="any", inplace=True)
    for col in must:
        df[col] = df[col].apply(lambda x: None if is_filth(x) else x)
        df.dropna(subset=[col], inplace=True)

    if "unixReviewTime" in df.columns:
        df["unixReviewTime"] = df["unixReviewTime"].fillna(
            datetime.datetime.now().timestamp()
        )
    else:
        df["unixReviewTime"] = datetime.datetime.now().timestamp()

    if "vote" not in df.columns:
        df["vote"] = 0
    if "style" not in df.columns:
        df["style"] = ""
    if "image" not in df.columns:
        df["image"] = ""
    if "summary" not in df.columns:
        df["summary"] = ""

    df["verified"] = (
        df["verified"].fillna(0).apply(lambda x: False if is_filth(x) else bool(x))
    )
    df["summary"] = df["summary"].fillna(0).apply(lambda x: "" if is_filth(x) else x)
    df["image"] = df["image"].fillna(0).apply(lambda x: "" if is_filth(x) else x)
    df["style"] = df["style"].fillna(0).apply(lambda x: "" if is_filth(x) else x)
    df["vote"] = df["vote"].apply(filter_int).fillna(0)
    return df
