from typing import Dict
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
    overall = models.PositiveSmallIntegerField(null=False, blank=False)
    reviewText = models.TextField(null=False, blank=True, default="")
    reviewerID = models.CharField(max_length=255, unique=False, null=False, blank=False)
    reviewerName = models.CharField(max_length=255, null=False, blank=False)
    summary = models.TextField(null=False, blank=True, default="")
    unixReviewTime = models.PositiveBigIntegerField(null=False, blank=False)
    verified = models.BooleanField(default=False)
    style = models.JSONField(null=True, blank=True)
    vote = models.PositiveSmallIntegerField(null=True, blank=True)
    image = models.JSONField(null=True, blank=True)

    class Meta:
        unique_together = ("asin", "reviewerID")


class ReviewEmotionsModel(APIModelStructure, models.Model):
    asin = models.CharField(
        max_length=255, unique=False, null=False, blank=False, db_index=True
    )
    reviewerID = models.CharField(
        max_length=255, unique=False, null=False, blank=False, db_index=True
    )
    overall = models.FloatField(null=False, blank=False)
    anger = models.FloatField(null=False, blank=False)
    disgust = models.FloatField(null=False, blank=False)
    fear = models.FloatField(null=False, blank=False)
    joy = models.FloatField(null=False, blank=False)
    neutral = models.FloatField(null=False, blank=False)
    sadness = models.FloatField(null=False, blank=False)
    surprise = models.FloatField(null=False, blank=False)

    class Meta:
        unique_together = ("asin", "reviewerID")


class PCAEncodedReviewEmotionsModel(APIModelStructure, models.Model):
    asin = models.CharField(
        max_length=255, unique=False, null=False, blank=False, db_index=True
    )
    reviewerID = models.CharField(
        max_length=255, unique=False, null=False, blank=False, db_index=True
    )
    vec_d1 = models.FloatField(null=False, blank=False)
    vec_d2 = models.FloatField(null=False, blank=False)
    vec_d3 = models.FloatField(null=False, blank=False)
    vec_d4 = models.FloatField(null=False, blank=False)

    class Meta:
        unique_together = ("asin", "reviewerID")
