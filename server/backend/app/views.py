"""
Endpoints REST
"""
from app.data_models.apistructure import APIViewStructure, ApiResponse, ApiViewMetaClass
from app.models import *
import json
import pandas as pd
import re
import datetime


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


class AmazonMetadataView(APIViewStructure, metaclass=ApiViewMetaClass):
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
        # TODO: date is in format 'MMMM DD, YYYY' not in ISO
        df["date"].apply(lambda x: datetime.datetime.fromisoformat(x.split("Z")[0]))
        entries = df.apply(
            lambda row: AmazonMetadataModel(
                asin=row["asin"],
                also_buy=row["also_buy"],
                also_view=row["also_view"],
                brand=row["brand"],
                category=row["category"],
                date=row["date"],
                description=row["description"],
                details=row["details"],
                feature=row["feature"],
                image=row["image"],
                main_cat=row["main_cat"],
                price=row["price"],
                rank=row["rank"],
                tech1=row["tech1"],
                tech2=row["tech2"],
                title=row["title"],
            )
        ).to_list()

        AmazonMetadataModel.objects.bulk_create(entries)

        return ApiResponse(success=True, code=201, data="something")


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
        df = pd.DataFrame(json.loads(request.data))
        df["rank"].apply(lambda x: int(re.findall(r"\d+", x.replace(",", ""))[0]))
        return ApiResponse(success=True, code=201, data="something")
