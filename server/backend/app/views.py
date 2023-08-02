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
                .values("asin", "reviewerID", "overall", "reviewText", "summary")
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
        df = pd.DataFrame(
            data, index=data["asin"] if isinstance(data["asin"], list) else [0]
        )
        parsed = time.time()
        print(f"parsing took: {parsed - start_request}")
        df.drop_duplicates(subset=["asin", "reviewerID"], inplace=True)
        if (
            any(
                df["asin"].apply(
                    lambda x: True
                    if isinstance(x, float) or x.lower() == "nan"
                    else False
                )
            )
            or any(
                df["overall"].apply(lambda x: True if isinstance(x, float) else False)
            )
            or any(
                df["reviewerID"].apply(lambda x: True if x.lower() == "nan" else False)
            )
        ):
            raise Exception("why is this data so ugly", 400)
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
        if "reviewText" not in df.columns:
            df["reviewText"] = ""
        if "summary" not in df.columns:
            df["summary"] = ""

        df["verified"] = df["verified"].apply(lambda x: bool(x))
        df["reviewText"] = df["reviewText"].apply(
            lambda x: "" if x is None or x.lower() == "nan" else x
        )
        df["reviewerName"] = df["reviewerName"].apply(
            lambda x: "" if x is None or x.lower() == "nan" else x
        )
        df["summary"] = df["summary"].apply(
            lambda x: "" if x is None or x.lower() == "nan" else x
        )
        df["image"] = df["image"].apply(
            lambda x: "" if x is None or x.lower() == "nan" else x
        )
        df["style"] = df["style"].apply(
            lambda x: "" if x is None or x.lower() == "nan" else x
        )
        df["vote"] = df["vote"].fillna(0)
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

        Notes
        -----
        in the end I'm only using overall, anger, disgust, joy for vector search
        because postgis only supports up to 4D vectors. And Its already been a lot
        of work getting this functional without changing any table, I don't want to migrate to pgvector
        where I would have to create and populate a new table
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
        pca = PCAEncodedReviewEmotionsView.pca
        if pca is None:
            PCAEncodedReviewEmotionsView.update_pca()
            pca = PCAEncodedReviewEmotionsView.pca
        vector = pca.transform(
            [overall, anger, disgust, fear, joy, neutral, sadness, surprise]
        )
        sql = f"""
        WITH top_k as (
            SELECT 1 as id, a.asin, a.reviewerID FROM (
                SELECT review_emotion, ST_MakePoint(vec_d1, vec_d2, vec_d3, vec_d4) as vect
                FROM app_pcaencodedreviewemotionsmodel
                ORDER BY asin
            ) as a
            ORDER BY a.vect <-> ST_MakePoint({", ".join(vector)})
            LIMIT %s
        )

        SELECT 1 as id, a.reviewerID, a.asin
        FROM app_reviewemotionsmodel as a
        WHERE a.asin = top_k.asin and a.reviewerID = top_k.reviewerID;
        """
        objs = ReviewEmotionsModel.objects.raw(sql, params=[k])
        return ApiResponse(success=True, code=200, data=[obj.asin for obj in objs])

    def post(self, request, *args, **kwargs):
        """Creates a single instance of a Review Emotion Model

        Parameters
        ----------
        body: `Dict`
            - asin: str
            - reviewerID: str
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
        print(data)

        if (
            ReviewEmotionsModel.objects.filter(reviewerID=data["reviewerID"])
            .filter(asin=data["asin"])
            .exists()
        ):
            return ApiResponse(success=True, code=200, data="exists")
        ReviewEmotionsModel.objects.create(**data)
        return ApiResponse(success=True, code=201, data="created")


class PCAEncodedReviewEmotionsView(APIViewStructure, metaclass=ApiViewMetaClass):
    """Endpoint for PCA(n_components=4) encoded Review Emotions"""

    pca = None

    def get(self, request, *args, **kwargs):
        data = request.data
        if self.pca is None:
            PCAEncodedReviewEmotionsView.update_pca()
            self.pca = PCAEncodedReviewEmotionsView.pca
        return ApiResponse(
            success=True,
            code=200,
            data=pd.DataFrame(self.pca.transform(data)).to_json(),
        )

    def update(self, request, *args, **kwargs):
        PCAEncodedReviewEmotionsView.update_pca()
        return ApiResponse(success=True, code=200, data="")

    @classmethod
    def update_pca(cls):
        from sklearn.decomposition import PCA
        from django.db import connection

        pca = cls.pca if cls.pca is not None else PCA(n_components=4)

        dimensions = [
            "overall",
            "anger",
            "disgust",
            "fear",
            "joy",
            "neutral",
            "sadness",
            "surprise",
        ]
        table = pd.read_sql_table(
            "app_reviewemotionsmodel",
            connection,
            columns=["asin", "reviewerID", *dimensions],
        )
        subset = table[dimensions]
        table.drop(dimensions, inplace=True, axis=1)

        cls.pca = pca.fit(subset)
        df = pd.DataFrame(
            data=cls.pca.transform(subset),
            columns=["vec_d1", "vec_d2", "vec_d3", "vec_d4"],
        )
        results = table.join(df)
        df.drop(df.columns, inplace=True)
        table.drop(table.columns, inplace=True, axis=1)

        PCAEncodedReviewEmotionsModel.objects.bulk_update(
            [PCAEncodedReviewEmotionsModel(*data) for _, *data in results.itertuples()]
        )
