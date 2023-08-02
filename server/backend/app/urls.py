from .views import *
from django.urls import path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/swagger",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger",
    ),
    path("amazon_metadata", AmazonMetadataView.as_view(), name="amazon_metadata"),
    path("amazon_review", AmazonReviewView.as_view(), name="amazon_review"),
    path("review_emotions", ReviewEmotionsView.as_view(), name="review_emotions"),
    path(
        "pca_embeddings", PCAEncodedReviewEmotionsView.as_view(), name="pca_embeddings"
    ),
]
