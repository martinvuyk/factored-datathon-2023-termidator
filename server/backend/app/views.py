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
from django.core import serializers


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


def filter_nan_in_str_field(df):
    return df.apply(lambda x: x if not isinstance(x, float) else None).apply(
        lambda x: x if x is not None else ""
    )


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

    def post(self, request, *args, **kwargs):
        """Creates AmazonMetadataModel instances in the DB

        Parameters
        ----------
        body: `Dict`
            - asin: `str`
            - also_buy: `List[str]`
            - also_view: `List[str]`
            - brand: `str`
            - category: `str`
            - date: `str`
            - description: `str`
            - details: `str`
            - feature: `List[str]`
            - image: `List[str]`
            - main_cat: `str`
            - price: `int`
            - rank: `str`
            - title: `str`

        Returns
        -------
        ret: `ApiResponse`:
            - success: ``True``
            - data: ``"total time: {time.time() - start_request}"``
            - code: 201
        """

        print("recieved request")
        start_request = time.time()
        data = json.loads(request.data)
        df = pd.DataFrame(data, index=data["asin"])
        parsed = time.time()
        print(f"parsing took: {parsed - start_request}")
        df.drop_duplicates(subset=["asin"], inplace=True)
        df["details"] = df["details"].apply(lambda x: x if x is not None else "")
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
                brand=row.brand[:255],
                category=row.category,
                date=row.date,
                description=row.description,
                details=row.details,
                feature=row.feature,
                image=row.image,
                main_cat=row.main_cat[:255],
                price=row.price,
                rank=row.rank,
                title=row.title[:255],
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
        """Returns the ids of all reviews in db if asin=None in query_params

        Parameters
        ----------
        query_params: `Dict`
            - asin: `Optional[str]`
        Returns
        -------
        ret: `ApiResponse`:
            - success: ``True``
            - data: `List[str] | Dict`
            - code: 201
        """
        params = request.query_params.get("asin")
        if params is None:
            return ApiResponse(
                success=True,
                code=200,
                data=list(
                    AmazonReviewModel.objects.values_list("asin", flat=True)
                    .distinct()
                    .order_by()
                ),
            )
        return ApiResponse(
            success=True,
            code=200,
            data=[
                row
                for row in AmazonReviewModel.objects.filter(asin=params)
                .values("asin", "overall", "reviewText", "summary")
                .all()
            ],
        )

    def post(self, request, *args, **kwargs):
        """Creates AmazonReviewModel instances in the DB

        Parameters
        ----------
        body: `Series[Dict]`
            - asin: `str`
            - overall: `float`
            - reviewText: `str`
            - reviewerID: `str`
            - reviewerName: `str`
            - summary: `str`
            - unixReviewTime: `int`
            - verified: `bool`
            - style: `str`
            - vote: `int`
            - image: `str`

        Returns
        -------
        ret: `ApiResponse`:
            - success: ``True``
            - data: ``"total time: {time.time() - start_request}"``
            - code: 201
        """

        print("recieved request")
        start_request = time.time()
        data = json.loads(request.data)
        if "asin" not in data.keys():
            raise Exception("review_has_no_asin", 400)
        df = pd.DataFrame(
            data, index=data["asin"] if isinstance(data["asin"], list) else [0]
        )
        parsed = time.time()
        print(f"parsing took: {parsed - start_request}")
        df.drop_duplicates(subset=["asin"], inplace=True)
        if "unixReviewTime" in df:
            df["unixReviewTime"] = df["unixReviewTime"].fillna(
                datetime.datetime.now().timestamp()
            )
        else:
            df["unixReviewTime"] = datetime.datetime.now().timestamp()
        if "vote" not in df:
            df["vote"] = 0
        if "style" not in df:
            df["style"] = ""
        if "image" not in df:
            df["image"] = ""
        if "reviewText" not in df:
            df["reviewText"] = ""
        if "summary" not in df:
            df["summary"] = ""

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
        df["vote"] = df["vote"].fillna(0)
        df["style"] = filter_nan_in_str_field(df["style"])
        df["image"] = filter_nan_in_str_field(df["image"])
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


class ReviewEmotionsView(APIViewStructure, metaclass=ApiViewMetaClass):
    """Endpoint for Review Emotions"""

    def get(self, request, *args, **kwargs):
        """Returns k nearest neighbors ("asin") to given emotion review

        Parameters
        ----------
        query_params: `Dict`
            - k: int
            - overall: float
            - anger: float
            - disgust: float
            - fear: float
            - joy: float
            - neutral: float
            - sadness: float
            - surprise: float
        Returns
        -------
        ret: `ApiResponse`:
            - success: ``True``
            - data: `List[str]`
            - code: 200
        """
        k, overall, anger, disgust, fear, joy, neutral, sadness, surprise = (
            request.query_params.get("k"),
            request.query_params.get("overall"),
            request.query_params.get("anger"),
            request.query_params.get("disgust"),
            request.query_params.get("fear"),
            request.query_params.get("joy"),
            request.query_params.get("neutral"),
            request.query_params.get("sadness"),
            request.query_params.get("surprise"),
        )
        param = ", ".join(
            # [overall, anger, disgust, fear, joy, neutral, sadness, surprise]
            [overall, anger, disgust, joy]
        )

        sql = f"""
        SELECT 1 as id, a.asin FROM (
            SELECT asin, ST_MakePoint(overall, anger, disgust, joy) as vect
            FROM app_reviewemotionsmodel
            ORDER BY asin
        ) as a
        ORDER BY a.vect <-> ST_MakePoint({param})
        LIMIT %s;
        """
        objs = ReviewEmotionsModel.objects.raw(sql, params=[k])
        return ApiResponse(success=True, code=200, data=[obj.asin for obj in objs])

    def post(self, request, *args, **kwargs):
        """Creates a single instance of a Review Emotion Model

        Parameters
        ----------
        body: `Dict`
            - asin: str
            - overall: float
            - anger: float
            - disgust: float
            - fear: float
            - joy: float
            - neutral: float
            - sadness: float
            - surprise: float
        Returns
        -------
        ret: `ApiResponse`:
            - success: ``True``
            - data: ``"something"``
            - code: 201
        """

        data = json.loads(request.data)

        message = "exists"
        if (
            not ReviewEmotionsModel.objects.filter(asin=data["asin"])
            .filter(**data)
            .exists()
        ):
            ReviewEmotionsModel.objects.create(**data)
            message = "created"

        return ApiResponse(success=True, code=201, data=message)
