from django.contrib import admin
from app.models import AmazonMetadataModel, AmazonReviewModel, ReviewEmotionsModel

admin.site.register(AmazonMetadataModel)
admin.site.register(AmazonReviewModel)
admin.site.register(ReviewEmotionsModel)
