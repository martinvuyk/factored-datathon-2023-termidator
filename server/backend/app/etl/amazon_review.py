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
    """This is ridiculous"""
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
    if df.empty:
        return df
    is_filth = im_sick_of_this_dataset
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(subset=must, how="any", inplace=True)

    # yeah.. so sometimes one of these comes with more than 255 chars for some reason
    longer_255 = lambda x: None if len(x) > 255 else x

    # and some stuff is just plain contaminated
    def replace_nul(item=""):
        return lambda x: x.replace("\x00", "") if isinstance(x, str) else item

    for col in must:
        if col not in ["reviewText", "overall"]:
            df[col] = df[col].apply(longer_255)
        df[col] = df[col].apply(lambda x: None if is_filth(x) else x)
        if col != "overall":
            df[col] = df[col].apply(replace_nul(None))
        df.dropna(subset=[col], how="any", inplace=True)

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

    is_filth_string = lambda x: "" if is_filth(x) else x
    df["verified"] = (
        df["verified"].fillna(0).apply(lambda x: False if is_filth(x) else bool(x))
    )
    df["summary"] = df["summary"].fillna(0).apply(is_filth_string).apply(replace_nul())
    df["image"] = df["image"].fillna(0).apply(is_filth_string).apply(replace_nul())
    df["style"] = df["style"].fillna(0).apply(is_filth_string).apply(replace_nul())
    df["vote"] = df["vote"].apply(filter_int).fillna(0)
    return df
