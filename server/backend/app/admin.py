from django.contrib import admin
from app.models import AmazonMetadataModel, AmazonReviewModel

admin.site.register(AmazonMetadataModel)
admin.site.register(AmazonReviewModel)
