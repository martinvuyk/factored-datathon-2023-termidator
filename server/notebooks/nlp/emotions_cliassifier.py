from transformers import pipeline
import requests
import asyncio
import os
import json
from typing import TypedDict, List
import random
import time
import logging

logging.basicConfig(level="INFO")

BACKEND_SERVER = f"{os.getenv('BACKEND_HOST', 'http://localhost')}:{os.getenv('BACKEND_PORT', '4595')}"


class ClassifierResult(TypedDict):
    label: str
    score: float


def get_knn_from_single_random_review():
    classifier = pipeline(
        "text-classification",
        model="j-hartmann/emotion-english-distilroberta-base",
        top_k=7,
    )
    """https://huggingface.co/j-hartmann/emotion-english-distilroberta-base"""
    review_ids = requests.get(
        f"{BACKEND_SERVER}/api/v1/amazon_review", params={"asin": None}
    ).json()["data"]

    review_asin_id = random.choice(review_ids)
    # TODO: have to store this as json cause waiting 1 minute for a list just to take 1 is dumb
    review = requests.get(
        f"{BACKEND_SERVER}/api/v1/amazon_review", params={"asin": review_asin_id}
    ).json()["data"][0]
    review_text = f"{review['reviewText']} {review['summary']}"[:512]
    results: List[ClassifierResult] = classifier(review_text)[0]
    data = {result["label"]: result["score"] for result in results}
    result = dict(overall=review["overall"], **data)

    resp = requests.get(
        f"{BACKEND_SERVER}/api/v1/review_emotions",
        params={"k": 5, **result},
    )
    logging.info(resp.json())


async def post_result(classifier, asin: str):
    batch_start = time.time()
    server_data = requests.get(
        f"{BACKEND_SERVER}/api/v1/amazon_review", params={"asin": asin}
    ).json()["data"]
    for review in server_data:
        review_text = f"{review['reviewText']} {review['summary']}"[:512]
        results: List[ClassifierResult] = classifier(review_text)[0]
        data = {result["label"]: result["score"] for result in results}

        result = dict(
            asin=asin,
            reviewerID=review["reviewerID"],
            overall=review["overall"],
            **data,
        )
        resp = requests.post(
            f"{BACKEND_SERVER}/api/v1/review_emotions",
            json=json.dumps(result),
        )
        logging.info(resp.json())
    logging.info(f"batch_time: {asin} -> {time.time() - batch_start}")


async def main():
    start = time.time()
    classifier = pipeline(
        "text-classification",
        model="j-hartmann/emotion-english-distilroberta-base",
        top_k=7,
    )
    """https://huggingface.co/j-hartmann/emotion-english-distilroberta-base"""
    reviews = requests.get(
        f"{BACKEND_SERVER}/api/v1/amazon_review", params={"asin": None}
    ).json()["data"]
    logging.info(f"got reviews: {len(reviews)}")
    for review in reviews:
        asyncio.create_task(post_result(classifier, review["asin"]))

        if len(asyncio.all_tasks()) - 1 > 16:
            # wait for the first 4 tasks that were triggered
            all_tasks = asyncio.all_tasks()
            all_tasks.remove(asyncio.current_task())
            await asyncio.wait(list(all_tasks)[:4])

    all_tasks = asyncio.all_tasks()
    all_tasks.remove(asyncio.current_task())
    await asyncio.wait(all_tasks)
    logging.info(f"total time elapsed: {time.time() - start}")


if __name__ == "__main__":
    asyncio.run(main())
    # get_knn_from_single_random_review()
