"""
URL mappings for the image API.
"""

from django.urls import path
from . import views

app_name = "image"

urlpatterns = [
    path("images/", views.ImageAPIView.as_view(), name="image-list"),
    path("images/<int:pk>/", views.DetailImageAPIView.as_view(), name="image-detail"),
    path(
        "images/resize/",
        views.CreateImageResizedAPIView.as_view(),
        name="resized-create",
    ),
    path(
        "images/resize/<int:pk>/", views.GetResizedAPIView.as_view(), name="resized-get"
    ),
    path("resized/", views.ResizedAPIView.as_view(), name="resized-list"),
    path(
        "resized/<int:pk>/", views.DetailResizedAPIView.as_view(), name="resized-detail"
    ),
    path(
        "resized/link/<int:pk>/",
        views.LinkViewSet.as_view({"get": "retrieve"}),
        name="resized-expiring",
    ),
    path(
        "images/link/<int:pk>/",
        views.LinkViewSet.as_view({"get": "retrieve"}),
        name="images-expiring",
    ),
]
