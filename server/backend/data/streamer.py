from json_gz_converter import json_gz_to_df, json_gz_to_iterable
import os
import requests
import time
import json

BATCH_DIR = "./blobs"
STREAM_DIR = "./stream"
BATCH_FILES = [filename for filename in os.listdir(BATCH_DIR) if ".json.gz" in filename]
BACKEND_SERVER = f"{os.getenv('BACKEND_HOST', 'http://localhost')}:{os.getenv('BACKEND_PORT', '4595')}"


def post_to_endpoint(metadata=True):
    if metadata:
        endpoint = "amazon_metadata"
        partitions = [filename for filename in BATCH_FILES if "metadata" in filename]
    else:
        endpoint = "amazon_review"
        partitions = [filename for filename in BATCH_FILES if "review" in filename]
    start = time.time()
    for partition in partitions:
        start_partition = time.time()
        payload = json_gz_to_df(f"{BATCH_DIR}/{partition}").to_json()
        print(f"time to prepare payload: {time.time() - start_partition}")
        resp = requests.post(
            f"{BACKEND_SERVER}/api/v1/{endpoint}",
            json=payload,
        )
        print(resp.json())
    print(f"total time elapsed: {time.time() - start}")


def get_amzn_reviews(field_list, metadata=True):
    if metadata:
        partitions = [filename for filename in BATCH_FILES if "metadata" in filename]
    else:
        partitions = [filename for filename in BATCH_FILES if "review" in filename]
    print(partitions[0])
    df = json_gz_to_df(f"{BATCH_DIR}/{partitions[0]}")
    print("dataset cols:\n")
    print(df.columns)
    print(df.shape)

    def get_field(field: str):
        return df[field].iloc[df[field].first_valid_index()]

    for field in field_list:
        print(f"{field}: {get_field(field)}")


def stream_to_endpoint():
    partition = "partition_0_2023_07_28.json.gz"
    for line in json_gz_to_iterable(f"{STREAM_DIR}/{partition}"):
        resp = requests.post(
            f"{BACKEND_SERVER}/api/v1/amazon_review",
            json=json.dumps(line),
        )
        print(resp.json())


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
post_to_endpoint(metadata=True)
# stream_to_endpoint()
