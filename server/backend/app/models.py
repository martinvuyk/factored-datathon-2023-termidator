from django.db import models
from django.utils import timezone
from app.data_models.apistructure import APIModelStructure


class AmazonMetadataModel(APIModelStructure, models.Model):
    asin = models.CharField(
        max_length=255, unique=True, null=False, blank=False, db_index=True
    )
    also_buy = models.JSONField()
    also_view = models.JSONField()
    brand = models.CharField(max_length=255, null=False, blank=False)
    category = models.JSONField()
    date = models.DateTimeField(null=True, blank=True, default=timezone.now)
    description = models.TextField(null=False, blank=True)
    details = models.TextField(null=True, blank=True)
    feature = models.JSONField()
    image = models.JSONField()
    main_cat = models.CharField(max_length=255, null=False, blank=False)
    price = models.IntegerField(null=True, blank=True)
    rank = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=255, null=False, blank=False)


class AmazonReviewModel(APIModelStructure, models.Model):
    asin = models.CharField(
        max_length=255, unique=False, null=False, blank=False, db_index=True
    )
    overall = models.FloatField(null=False, blank=False)
    reviewText = models.TextField(null=False, blank=True)
    reviewerID = models.CharField(max_length=255, unique=True, null=False, blank=False)
    reviewerName = models.CharField(max_length=255, null=False, blank=False)
    summary = models.TextField(null=False, blank=True)
    unixReviewTime = models.PositiveBigIntegerField(null=False, blank=False)
    verified = models.BooleanField(default=False)
    style = models.JSONField(null=True, blank=True)
    vote = models.PositiveSmallIntegerField(null=True, blank=True)
    image = models.JSONField(null=True, blank=True)
