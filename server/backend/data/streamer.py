from json_gz_converter import json_gz_to_df
import os
import requests
import time

DATA_DIR = "./blobs"
BATCH_FILES = [filename for filename in os.listdir(DATA_DIR) if ".json.gz" in filename]
BACKEND_SERVER = f"{os.getenv('BACKEND_HOST', 'http://localhost')}:{os.getenv('BACKEND_PORT', '4595')}"


def post_to_endpoint(metadata=True):
    if metadata:
        endpoint = "amazon_metadata"
        partitions = [filename for filename in BATCH_FILES if "metadata" in filename]
    else:
        endpoint = "amazon_review"
        partitions = [filename for filename in BATCH_FILES if "review" in filename]
    start = time.time()
    payload = json_gz_to_df(f"{DATA_DIR}/{partitions[0]}").to_json()
    print(f"time to prepare payload: {time.time() - start}")
    resp = requests.post(
        f"{BACKEND_SERVER}/api/v1/{endpoint}",
        json=payload,
    )
    print(resp.json())


def get_amzn_reviews(field_list, metadata=True):
    if metadata:
        partitions = [filename for filename in BATCH_FILES if "metadata" in filename]
    else:
        partitions = [filename for filename in BATCH_FILES if "review" in filename]
    print(partitions[0])
    df = json_gz_to_df(f"{DATA_DIR}/{partitions[0]}")
    print("dataset cols:\n")
    print(df.columns)
    print(df.shape)

    def get_field(field: str):
        return df[field].iloc[df[field].first_valid_index()]

    for field in field_list:
        print(f"{field}: {get_field(field)}")


amzn_reviews = [
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
amzn_metadata = [
    "also_buy",
    "also_view",
    "asin",
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
    "tech1",
    "tech2",
    "title",
]
# get_amzn_reviews(amzn_metadata)
# get_amzn_reviews(amzn_reviews, metadata=False)
post_to_endpoint(metadata=False)
