from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_file, name='upload'),
    path('search/', views.search, name='search'),
    path('collections/', views.collections, name='collections'),
    path('collections/<str:name>/', views.delete_collection, name='delete_collection'),
]