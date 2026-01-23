from django.urls import path
from .views import SearchView, CollectionInfoView, DocumentChunksView

urlpatterns = [
    path("search/", SearchView.as_view(), name="search"),
    path("collection-info/", CollectionInfoView.as_view(), name="collection-info"),
    path("document-chunks/", DocumentChunksView.as_view(), name="document-chunks"),
]