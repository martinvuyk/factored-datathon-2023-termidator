"""
Endpoints REST
"""
from app.data_models.apistructure import APIViewStructure, ApiResponse, ApiViewMetaClass
from app.models import *
import json
import pandas as pd
import time
from app.etl import amazon_review, amazon_metadata
from sklearn.decomposition import PCA
from django.db import connection
import logging


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

        logging.debug("recieved request")
        start_request = time.time()
        data = json.loads(request.data)
        df = pd.DataFrame(data, index=data["asin"])
        parsed = time.time()
        logging.debug(f"parsing took: {parsed - start_request}")
        df = amazon_metadata.clean(df)
        if df.empty:
            raise Exception("bad_data", 400)
        cleaning = time.time()
        logging.debug(f"cleaning took: {cleaning - parsed}")
        entries = [
            AmazonMetadataModel(**{col: val for col, val in zip(df.columns, row)})
            for _, *row in df.itertuples()
        ]
        creating = time.time()
        logging.debug(f"creating took: {creating - cleaning}")
        AmazonMetadataModel.objects.bulk_create(entries, ignore_conflicts=True)
        logging.debug(f"write to db took: {time.time() - creating}")
        return ApiResponse(
            success=True, code=201, data=f"total time: {time.time() - start_request}"
        )


class AmazonReviewView(APIViewStructure, metaclass=ApiViewMetaClass):
    def get(self, request, *args, **kwargs):
        """Returns all reviews for given asin, if asin=None then asin of all products with a review in db

        Parameters
        ----------
        query_params: `Dict`
            - asin: `Optional[str]`

        Returns
        -------
        ret: `ApiResponse`:
            - success: ``True``
            - data: `List[Dict]`
            - code: 201
        """
        logging.debug("revieved request")
        asin = request.query_params.get("asin")
        reviews = AmazonReviewModel.objects
        if asin is not None:
            start_filter = time.time()
            reviews = reviews.filter(asin=asin)
            end_filter = time.time()
            logging.debug(f"filtering took: {end_filter - start_filter}")
            values = ["asin", "reviewerID", "overall", "reviewText", "summary"]
            data = list(reviews.values(*values))
            logging.debug(f"list values took: {time.time() - end_filter}")
            return ApiResponse(success=True, code=200, data=data)
        else:
            start_list = time.time()
            products = list(AmazonMetadataModel.objects.values("asin"))
            logging.debug(f"get list took: {time.time() - start_list}")
            return ApiResponse(success=True, code=200, data=products)

    def post(self, request, *args, **kwargs):
        """Creates AmazonReviewModel instances in the DB. Works with single and multiple values

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

        logging.debug("recieved request")
        start_request = time.time()
        df = pd.read_json(request.data)
        parsed = time.time()
        logging.debug(f"parsing took: {parsed - start_request}")
        df = amazon_review.clean(df)
        if df.empty:
            raise Exception("bad_data", 400)
        cleaning = time.time()
        logging.debug(f"cleaning took: {cleaning - parsed}")
        entries = [
            AmazonReviewModel(**{col: val for col, val in zip(df.columns, row)})
            for _, *row in df.itertuples()
        ]
        creating = time.time()
        logging.debug(f"creating took: {creating - cleaning}")
        AmazonReviewModel.objects.bulk_create(entries, ignore_conflicts=True)
        logging.debug(f"write to db took: {time.time() - creating}")
        return ApiResponse(
            success=True, code=201, data=f"total time: {time.time() - start_request}"
        )


class ReviewEmotionsView(APIViewStructure, metaclass=ApiViewMetaClass):
    """Endpoint for Review Emotions"""

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

    def get(self, request, *args, **kwargs):
        """Returns a dataframe with insights for the given asin

        Parameters
        ----------
        query_params: `Dict`
            - asin: `str`
        """
        asin = request.query_params.get("asin")
        if asin is None:
            raise Exception("bad_data", 400)

        reviews = ReviewEmotionsModel.objects.filter(asin=asin)
        df = pd.DataFrame.from_records(reviews.values())
        df.drop_duplicates(inplace=True)  # just in case
        pca = PCA(2).fit_transform(df[self.dimensions])
        df.join(pd.DataFrame(data=pca, columns=["pca_d1", "pca_d2"]))

        return ApiResponse(success=True, code=200, data="")

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
        """Returns k nearest neighbors ("asin") to given emotion review, for products that have the same main category

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
        where I would have to create and populate a new table. And impleenting PCA would
        mean read the whole table or at least 100k rows to fit and then transform each row from emotion to 4D PCA.
        I don't have enough time to implement it properly
        """
        # data = request.data
        # if self.pca is None:
        #     PCAEncodedReviewEmotionsView.update_pca()
        #     self.pca = PCAEncodedReviewEmotionsView.pca
        # return ApiResponse(
        #     success=True,
        #     code=200,
        #     data=pd.DataFrame(self.pca.transform(data)).to_json(),
        # )
        data_format = ["k", *ReviewEmotionsView.dimensions]
        data = [request.query_params.get(d) for d in data_format]
        if any(d is None for d in data):
            raise Exception("bad_data", 400)
        k, *dimensions = data

        overall, anger, disgust, _, joy, *_ = dimensions
        vector = overall, anger, disgust, joy
        # pca = PCAEncodedReviewEmotionsView.pca
        # if pca is None:
        #     PCAEncodedReviewEmotionsView.update_pca()
        #     pca = PCAEncodedReviewEmotionsView.pca
        # vector = pca.transform(dimensions)

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
        return ApiResponse(
            success=True,
            code=200,
            data=[{"asin": obj.asin, "reviewerID": obj.reviewerID} for obj in objs],
        )

    def update(self, request, *args, **kwargs):
        PCAEncodedReviewEmotionsView.update_pca()
        return ApiResponse(success=True, code=200, data="")

    @classmethod
    def update_pca(cls):
        pca = cls.pca if cls.pca is not None else PCA(n_components=4)

        table = pd.read_sql_query(
            "SELECT * FROM app_reviewemotionsmodel aa LIMIT 100000", connection
        )
        subset = table[ReviewEmotionsView.dimensions]
        table.drop(ReviewEmotionsView.dimensions, inplace=True, axis=1)

        cls.pca = pca.fit(subset)
        df = pd.DataFrame(
            data=cls.pca.transform(subset),
            columns=["vec_d1", "vec_d2", "vec_d3", "vec_d4"],
        )
        results = table.join(df)
        df.drop(df.columns, inplace=True)
        table.drop(table.columns, inplace=True, axis=1)

        PCAEncodedReviewEmotionsModel.objects.bulk_update(
            [
                PCAEncodedReviewEmotionsModel(
                    **{col: val for col, val in zip(results.columns, data)}
                )
                for _, *data in results.itertuples()
            ]
        )
