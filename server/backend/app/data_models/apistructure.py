from dataclasses import asdict, dataclass
from django.db import models
from abc import abstractmethod
from typing import Any, Callable, Iterator, Dict, Optional
from rest_framework.views import APIView
from django.http import JsonResponse
import traceback
import os
import logging

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO").upper())


class APIModelStructure:
    """Estructura de los modelos en la DB"""

    @staticmethod
    def is_stored_in_DB(cls: models.Model, field: str, value: Any) -> bool:
        return cls.objects.filter(**{field: value}).exists()

    @abstractmethod
    def get_object_data() -> Dict:
        pass

    @staticmethod
    def get_objects_data(objects: Iterator["APIModelStructure"]):
        return [object.get_object_data() for object in objects]


@dataclass
class ApiResponse:
    """Format for the answer of every endpoint in the API"""

    success: bool
    code: int
    data: Optional[Any] = None
    error: Optional[str] = None


class ApiViewMetaClass(type):
    """MetaClass to add wrappers to every endpoint without having to write decorators all the time"""

    def __new__(self, name, bases, attrs):
        """if the class has a method post, get, put o delete, wrap it with @handle_http_errors"""
        methods = ["post", "get", "put", "delete", "patch"]
        for metodo in methods:
            if metodo in attrs:
                attrs[metodo] = self.handle_http_errors(attrs[metodo])
        return super(ApiViewMetaClass, self).__new__(self, name, bases, attrs)

    @staticmethod
    def handle_http_errors(fn: Callable) -> Callable:
        """Wrapper que ejecuta el codigo de cada request y se encarga de lidiar con las excepciones que
        va lenvantando el codigo"""

        def new_fn(request, *args, **kwargs):
            response: ApiResponse
            try:
                try:
                    response = fn(request, *args, **kwargs)
                except Exception as e:
                    if len(e.args) != 2:
                        raise Exception(str(e), 500)
                    raise
            except Exception as e:
                if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
                    traceback.print_exc()
                response = ApiResponse(
                    success=False, code=e.args[1], error=e.args[0][:255]
                )
            finally:
                logging.debug(str(response)[:255])
                return JsonResponse(asdict(response), status=response.code)

        # Get back the docstrings
        new_fn.__doc__ = fn.__doc__
        return new_fn


class APIViewStructure(APIView, metaclass=ApiViewMetaClass):
    """Structure for the views in the API"""

    no_disponible = Exception("endpoint_not_available", 405)

    def post(self, request, *args, **kwargs) -> ApiResponse:
        """Default endpoint

        Returns
        -------
        ret: `ApiResponse`:
            - success: ``False``
            - error: ``"endpoint_not_available"``
            - code: 405
        """
        raise self.no_disponible

    def get(self, request, *args, **kwargs) -> ApiResponse:
        """Default endpoint

        Returns
        -------
        ret: `ApiResponse`:
            - success: ``False``
            - error: ``"endpoint_not_available"``
            - code: 405
        """
        raise self.no_disponible

    def put(self, request, *args, **kwargs) -> ApiResponse:
        """Default endpoint

        Returns
        -------
        ret: `ApiResponse`:
            - success: ``False``
            - error: ``"endpoint_not_available"``
            - code: 405
        """
        raise self.no_disponible

    def delete(self, request, *args, **kwargs) -> ApiResponse:
        """Default endpoint

        Returns
        -------
        ret: `ApiResponse`:
            - success: ``False``
            - error: ``"endpoint_not_available"``
            - code: 405
        """
        raise self.no_disponible
