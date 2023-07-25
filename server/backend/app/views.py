"""
Endpoints REST
"""
from app.data_models.apistructure import APIViewStructure, ApiResponse, ApiViewMetaClass
from app.models import *
from app.helpers.try_bool import try_false_type_guard


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
