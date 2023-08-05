"""
REST Endpoints
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

    def get(self, request, *args, **kwargs):
        """Returns asin of all reviews for given main_cat, if main_cat is None -> all asin in db

        Parameters
        ----------
        query_params: `Dict`
            - main_cat: `str`

        Returns
        -------
        ret: `ApiResponse`:
            - success: ``True``
            - data: `List[Dict]`
            - code: 201
        """
        main_cat = request.query_params.get("main_cat")
        products = AmazonMetadataModel.objects
        if main_cat is not None:
            start_cat = time.time()
            products = products.filter(main_cat=main_cat)
            if not products.exists():
                raise Exception("main_cat not found", 404)
            logging.debug(f"get cat took: {time.time() - start_cat}")
        start_list = time.time()
        products = list(products.values("asin"))
        logging.debug(f"get list took: {time.time() - start_list}")
        return ApiResponse(success=True, code=200, data=products)

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
    """Endpoint for Amazon Reviews"""

    def get(self, request, *args, **kwargs):
        """Returns all reviews for given asin

        Parameters
        ----------
        query_params: `Dict`
            - asin: `str`

        Returns
        -------
        ret: `ApiResponse`:
            - success: ``True``
            - data: `List[Dict]`
            - code: 201
        """
        logging.debug("revieved request")
        asin = request.query_params.get("asin")
        if asin is None:
            raise Exception("bad_data", 400)
        reviews = AmazonReviewModel.objects
        start_filter = time.time()
        reviews = reviews.filter(asin=asin)
        end_filter = time.time()
        logging.debug(f"filtering took: {end_filter - start_filter}")
        values = ["asin", "reviewerID", "overall", "reviewText", "summary"]
        data = list(reviews.values(*values))
        logging.debug(f"list values took: {time.time() - end_filter}")
        return ApiResponse(success=True, code=200, data=data)

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
        """Returns a dataframe with the top 20 products for the given main_cat

        Parameters
        ----------
        query_params: `Dict`
            - main_cat: `str`

        Returns
        -------
        ret: `ApiResponse`:
            - success: ``True``
            - data: `List[Dict]`
            - code: 200

        Notes
        -----
        1. Get 50 product reviews
            - where main_cat is as specified
            - have rating >= 3 stars
            - order by the amount of reviews "emotionally pre-processed"
        2. Order those reviews, get top 20
            1. order by rounding the rating (4.5+ -> 5, [3.5, 4.5] -> 4, etc.) desc
            2. order by the avg amount of joy desc
        """
        main_cat = request.query_params.get("main_cat")
        if main_cat is None:
            raise Exception("bad_data", 400)

        query = """
        select 	1 as id, row_number() over (partition by 1) as place, * from(
        select * from (
            select 
                asin, 
                count(*) as amount,
                sum(overall)/count(*) as overall, 
                sum(anger)/count(*) as anger, 
                sum(disgust)/count(*) as disgust, 
                sum(fear)/count(*) as fear, 
                sum(joy)/count(*) as joy,
                sum(neutral)/count(*) as neutral,
                sum(sadness)/count(*) as sadness,
                sum(surprise)/count(*) as surprise
            from app_reviewemotionsmodel ar 
            where asin in (select asin from app_amazonmetadatamodel aa where aa.main_cat = %s) 
                and overall >= 3
            group by asin order by amount desc
            limit 50
        ) aa
        order by round(overall) desc, joy desc
        limit 20) bb
        """
        objs = ReviewEmotionsModel.objects.raw(query, params=[main_cat])
        cols = ["place", "asin", "amount", *ReviewEmotionsView.dimensions]
        top_20 = [{col: getattr(obj, col) for col in cols} for obj in objs]
        return ApiResponse(success=True, code=200, data=top_20)

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
            - data: ``"created"``
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

    def get(self, request, *args, **kwargs):
        """Gets the most "emotionally average" review for a given asin

        Parameters
        ----------
        query_params: `Dict`
            - asin: `str`

        Returns
        -------
        ret: `ApiResponse`:
            - success: ``True``
            - data: `List[str]`
            - code: 200
        """
        asin = request.query_params.get("asin")
        if asin is None:
            raise Exception("bad_data", 400)
        start_asin = time.time()
        reviews = PCAEncodedReviewEmotionsModel.objects.filter(asin=asin)
        end_asin = time.time()
        logging.debug(f"getting asin pca took: {end_asin - start_asin}")
        if not reviews.exists():
            raise Exception("asin_not_processed", 400)

        d1, d2, d3, d4 = (
            [rev.vec_d1 for rev in reviews],
            [rev.vec_d2 for rev in reviews],
            [rev.vec_d3 for rev in reviews],
            [rev.vec_d4 for rev in reviews],
        )
        vector = (
            sum(d1) / len(d1),
            sum(d2) / len(d2),
            sum(d3) / len(d3),
            sum(d4) / len(d4),
        )

        sql = f"""
        WITH most_avg as (
            SELECT 1 as id, a.asin, a."reviewerID" FROM (
                SELECT asin, "reviewerID", ST_MakePoint(vec_d1, vec_d2, vec_d3, vec_d4) as vect
                FROM app_pcaencodedreviewemotionsmodel
                WHERE asin = %s
            ) as a
            ORDER BY a.vect <-> ST_MakePoint{vector}
            LIMIT 1
        )

        SELECT 1 as id, a."reviewerID", a.asin, a."reviewText"
        FROM app_amazonreviewmodel as a
        INNER JOIN most_avg ON a.asin = most_avg.asin and a."reviewerID" = most_avg."reviewerID";
        """
        obj = ReviewEmotionsModel.objects.raw(sql, params=[asin])[0]
        get_closest = time.time()
        logging.debug(f"getting closest took: {get_closest - end_asin}")
        cols = ["asin", "reviewerID", "reviewText"]
        avg = {col: getattr(obj, col) for col in cols}
        return ApiResponse(success=True, code=200, data=avg)

    def patch(self, request, *args, **kwargs):
        """Updates the pca representation for a given asin

        Parameters
        ----------
        query_params: `Dict`
            - asin: `str`

        Returns
        -------
        ret: `ApiResponse`:
            - success: ``True``
            - data: ``"updated"``
            - code: 200
        """
        asin = request.query_params.get("asin")
        if asin is None:
            raise Exception("bad_data", 400)
        self.update_pca(asin)
        return ApiResponse(success=True, code=200, data="updated")

    @staticmethod
    def update_pca(asin: str):
        pca = PCA(n_components=4)
        dims = ReviewEmotionsView.dimensions

        start_read = time.time()
        query = f"SELECT * FROM app_reviewemotionsmodel aa WHERE asin = %s"
        table = pd.read_sql_query(query, connection, params=[asin])
        if table.shape[0] < 4:
            raise Exception("not_enough_reviews", 404)
        end_read = time.time()
        logging.debug(f"read from db took: {end_read - start_read}")

        subset = table[dims]
        table.drop(dims, inplace=True, axis=1)

        vecs = ["vec_d1", "vec_d2", "vec_d3", "vec_d4"]
        df = pd.DataFrame(data=pca.fit_transform(subset), columns=vecs)
        end_pca_transf = time.time()
        logging.debug(f"building pca took: {end_pca_transf - end_read}")

        results = table.join(df)
        df.drop(df.columns, inplace=True, axis=1)
        table.drop(table.columns, inplace=True, axis=1)
        entries = [
            PCAEncodedReviewEmotionsModel(
                **{col: val for col, val in zip(results.columns, data)}
            )
            for _, *data in results.itertuples()
        ]
        end_build = time.time()
        logging.debug(f"building entries took: {end_build - end_pca_transf}")

        PCAEncodedReviewEmotionsModel.objects.bulk_create(
            entries, update_conflicts=True, unique_fields=["id"], update_fields=vecs
        )
        results.drop(results.columns, inplace=True, axis=1)
        logging.debug(f"write to db took: {time.time() - end_build}")
