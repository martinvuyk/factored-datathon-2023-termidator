from django.db import models
from app.data_models.apistructure import APIModelStructure


class SomethingModel(APIModelStructure, models.Model):
    uid = models.CharField(max_length=255, unique=True, null=False, blank=False)

    @classmethod
    def is_stored_in_DB(cls, uid):
        return APIModelStructure.is_stored_in_DB(cls, field="uid", value=uid)
