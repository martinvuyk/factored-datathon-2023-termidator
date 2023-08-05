import requests
import requests
import pandas as pd
import matplotlib.pyplot as plt
import os
import time

BASE_URL = f"http://{os.getenv('BACKEND_HOST', '127.0.0.1')}:4595/api/v1"


def update_pca(asin: str):
    resp = requests.patch(f"{BASE_URL}/pca_embeddings", params={"asin": asin}).json()
    print(resp)


def update_all_pcas():
    main_cat = "Toys & Games"
    start = time.time()
    products = requests.get(
        f"{BASE_URL}/amazon_metadata", params={"main_cat": main_cat}
    ).json()["data"]
    for product in products:
        update_pca(product["asin"])
    print(f"updating all pca for '{main_cat}' took: {time.time() - start}")


def get_most_avg_review(asin: str):
    resp = requests.get(f"{BASE_URL}/pca_embeddings", params={"asin": asin}).json()
    return resp["data"]


def get_most_relevant_products(main_cat: str):
    url = f"{BASE_URL}/review_emotions"
    resp = requests.get(url, params={"main_cat": main_cat}).json()
    return resp["data"]


if __name__ == "__main__":
    # update_all_pcas()
    products = get_most_relevant_products("Toys & Games")
    for product in products:
        print(product["asin"])
        update_pca(product["asin"])
        print(get_most_avg_review(product["asin"]))
