from json_gz_converter import json_gz_to_df, json_gz_to_iterable
import os
import requests
import time
import json
import asyncio
from typing import List

BATCH_DIR = "./blobs"
STREAM_DIR = "./stream"
BATCH_FILES = [filename for filename in os.listdir(BATCH_DIR) if ".json.gz" in filename]
BACKEND_SERVER = f"{os.getenv('BACKEND_HOST', 'http://localhost')}:{os.getenv('BACKEND_PORT', '4595')}"

amzn_reviews = [
    "asin",
    "reviewerID",
    "overall",
    "reviewText",
    "reviewerName",
    "summary",
    "unixReviewTime",
    "verified",
    "style",
    "vote",
    "image",
]
amzn_metadata = [
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


async def parse_and_send(partition: str, endpoint: str, cols: List[str]):
    start_partition = time.time()
    df = json_gz_to_df(f"{BATCH_DIR}/{partition}")
    if "asin" not in df.columns:
        return
    if endpoint == "amazon_review" and (
        "reviewerID" not in df.columns
        or "overall" not in df.columns
        or "reviewText" not in df.columns
    ):
        return
    df.drop(columns=df.columns.difference(cols), inplace=True)
    payload = df.to_json()
    print(f"time to prepare payload: {time.time() - start_partition}")
    resp = requests.post(
        f"{BACKEND_SERVER}/api/v1/{endpoint}",
        json=payload,
    )
    print(resp.json())


async def post_to_endpoint(metadata=True):
    if metadata:
        endpoint = "amazon_metadata"
        partitions = [filename for filename in BATCH_FILES if "metadata" in filename]
        cols = amzn_metadata
    else:
        endpoint = "amazon_review"
        partitions = [filename for filename in BATCH_FILES if "review" in filename]
        cols = amzn_reviews
    start = time.time()
    for partition in partitions:
        asyncio.create_task(parse_and_send(partition, endpoint, cols))
    await asyncio.wait(asyncio.all_tasks())
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


# get_amzn_reviews(amzn_metadata)
# get_amzn_reviews(amzn_reviews, metadata=False)
asyncio.run(post_to_endpoint(metadata=False))
# stream_to_endpoint()
