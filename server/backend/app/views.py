"""
Endpoints REST
"""
from app.data_models.apistructure import APIViewStructure, ApiResponse, ApiViewMetaClass
from app.models import *
import json
import pandas as pd
import re
import datetime
import time


class SomethingView(APIViewStructure, metaclass=ApiViewMetaClass):
    """Endpoint for something"""

    def get(self, request, *args, **kwargs):
        """Returns Something

        Returns
        -------
        ret: `ApiResponse`:
            - success: ``True``
            - data: ``"something"``
            - code: 200
        """
        return ApiResponse(success=True, code=200, data="something")

    def post(self, request, *args, **kwargs):
        df = pd.DataFrame(json.loads(request.data))
        print(df.columns)
        return ApiResponse(success=True, code=201, data="something")


def filter_date(date: str):
    try:
        datetime.datetime.strptime(date, "%B %d, %Y")
    except ValueError:
        return None


def filter_int(string: str):
    if string is not None or string != "":
        numbers = re.findall(r"\d+", string.replace(",", ""))
        return numbers[0] if len(numbers) > 0 else None
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


class AmazonMetadataView(APIViewStructure, metaclass=ApiViewMetaClass):
    """Endpoint for Amazon Metadata"""

    def get(self, request, *args, **kwargs):
        """Returns Something

        Returns
        -------
        ret: `ApiResponse`:
            - success: ``True``
            - data: ``"something"``
            - code: 200
        """
        return ApiResponse(success=True, code=200, data="something")

    def post(self, request, *args, **kwargs):
        print("recieved request")
        start_request = time.time()
        data = json.loads(request.data)
        df = pd.DataFrame(data, index=data["asin"])
        parsed = time.time()
        print(f"parsing took: {parsed - start_request}")
        df.drop_duplicates(subset=["asin"], inplace=True)
        df["date"] = df["date"].apply(filter_date)
        df["rank"] = df["rank"].apply(filter_int).fillna(0).apply(lambda x: int(x))
        df["description"] = (
            df["description"]
            .apply(lambda x: x if x is not None else [""])
            .apply(lambda x: x[0] if len(x) > 0 else "")
        )
        df["price"] = df["price"].apply(filter_price).fillna(0)
        cleaning = time.time()
        print(f"cleaning took: {cleaning - parsed}")

        entries = [
            AmazonMetadataModel(
                asin=row.asin,
                also_buy=row.also_buy,
                also_view=row.also_view,
                brand=row.brand,
                category=row.category,
                date=row.date,
                description=row.description,
                details=row.details,
                feature=row.feature,
                image=row.image,
                main_cat=row.main_cat,
                price=row.price,
                rank=row.rank,
                title=row.title,
            )
            for row in df.itertuples()
        ]

        creating = time.time()
        print(f"creating took: {creating - cleaning}")

        AmazonMetadataModel.objects.bulk_create(entries, ignore_conflicts=True)

        print(f"write to db took: {time.time() - creating}")

        return ApiResponse(
            success=True, code=201, data=f"total time: {time.time() - start_request}"
        )


class AmazonReviewView(APIViewStructure, metaclass=ApiViewMetaClass):
    def get(self, request, *args, **kwargs):
        """Returns Something

        Returns
        -------
        ret: `ApiResponse`:
            - success: ``True``
            - data: ``"something"``
            - code: 200
        """
        return ApiResponse(success=True, code=200, data="something")

    def post(self, request, *args, **kwargs):
        print("recieved request")
        start_request = time.time()
        data = json.loads(request.data)
        df = pd.DataFrame(data, index=data["asin"])
        parsed = time.time()
        print(f"parsing took: {parsed - start_request}")
        df.drop_duplicates(subset=["asin"], inplace=True)
        df["unixReviewTime"] = df["unixReviewTime"].fillna(
            datetime.datetime.now().timestamp()
        )
        df["verified"] = df["verified"].apply(lambda x: bool(x))
        df["reviewText"] = df["reviewText"].apply(
            lambda x: "" if x is None or x == "null" else x
        )
        df["reviewerName"] = df["reviewerName"].apply(
            lambda x: "" if x is None or x == "null" else x
        )
        df["summary"] = df["summary"].apply(
            lambda x: "" if x is None or x == "null" else x
        )
        cleaning = time.time()
        print(f"cleaning took: {cleaning - parsed}")

        entries = [
            AmazonReviewModel(
                asin=row.asin,
                overall=row.overall,
                reviewText=row.reviewText,
                reviewerID=row.reviewerID,
                reviewerName=row.reviewerName,
                summary=row.summary,
                unixReviewTime=row.unixReviewTime,
                verified=row.verified,
                style=row.style,
                vote=row.vote,
                image=row.image,
            )
            for row in df.itertuples()
        ]

        creating = time.time()
        print(f"creating took: {creating - cleaning}")

        AmazonReviewModel.objects.bulk_create(entries, ignore_conflicts=True)

        print(f"write to db took: {time.time() - creating}")

        return ApiResponse(
            success=True, code=201, data=f"total time: {time.time() - start_request}"
        )
