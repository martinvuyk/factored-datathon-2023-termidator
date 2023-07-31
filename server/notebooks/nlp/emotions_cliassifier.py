from transformers import pipeline
import requests
import asyncio
import os
import json
from typing import TypedDict, List

BACKEND_SERVER = f"{os.getenv('BACKEND_HOST', 'http://localhost')}:{os.getenv('BACKEND_PORT', '4595')}"


class ClassifierResult(TypedDict):
    label: str
    score: float


async def post_result(classifier, review_id: str):
    server_data = requests.get(
        f"{BACKEND_SERVER}/api/v1/amazon_review", params={"asin": review_id}
    ).json()["data"]

    for review in server_data:
        review_text = f"{review['reviewText']} {review['summary']}"[:512]
        results: List[ClassifierResult] = classifier(review_text)[0]
        data = {result["label"]: result["score"] for result in results}

        result = dict(asin=review_id, overall=review["overall"], **data)
        resp = requests.post(
            f"{BACKEND_SERVER}/api/v1/review_emotions",
            json=json.dumps(result),
        )
        print(resp.json())


async def main():
    classifier = pipeline(
        "text-classification",
        model="j-hartmann/emotion-english-distilroberta-base",
        top_k=7,
    )
    """https://huggingface.co/j-hartmann/emotion-english-distilroberta-base"""
    review_ids = requests.get(
        f"{BACKEND_SERVER}/api/v1/amazon_review", params={"asin": None}
    ).json()["data"]
    for review_id in review_ids:
        asyncio.create_task(post_result(classifier, review_id))

    await asyncio.gather()


if __name__ == "__main__":
    asyncio.run(main())
