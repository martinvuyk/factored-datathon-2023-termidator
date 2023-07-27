from django.db import models
from app.data_models.apistructure import APIModelStructure


class AmazonMetadataModel(APIModelStructure, models.Model):
    asin = models.UUIDField(max_length=255, unique=True, null=False, blank=False)
    also_buy = models.JSONField()
    also_view = models.JSONField()
    brand = models.CharField(max_length=255, null=False, blank=False)
    category = models.JSONField()
    date = models.DateTimeField()
    description = models.CharField(max_length=255, null=False, blank=False)
    details = models.CharField(max_length=255, null=False, blank=False)
    feature = models.JSONField()
    image = models.URLField(max_length=200, null=False, blank=False)
    main_cat = models.CharField(max_length=255, null=False, blank=False)
    price = models.CharField(max_length=255, null=False, blank=False)
    rank = models.IntegerField()
    tech1 = models.CharField(max_length=255)
    tech2 = models.CharField(max_length=255)
    title = models.CharField(max_length=255, null=False, blank=False)


class AmazonReviewModel(APIModelStructure, models.Model):
    asin = models.UUIDField(max_length=255, unique=False, null=False, blank=False)
    overall = models.FloatField()
    reviewText = models.CharField(max_length=255, null=False, blank=True)
    reviewerID = models.UUIDField(max_length=255, unique=True, null=False, blank=False)
    reviewerName = models.CharField(max_length=255, null=False, blank=False)
    summary = models.CharField(max_length=255, null=False, blank=True)
    unixReviewTime = models.PositiveBigIntegerField(null=False, blank=False)
    verified = models.BooleanField(default=False)
    style = models.JSONField(null=True, blank=True)
    vote = models.PositiveSmallIntegerField(null=True, blank=True)
    image = models.JSONField(null=True, blank=True)
