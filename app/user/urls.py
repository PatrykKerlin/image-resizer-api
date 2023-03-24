"""
URL mappings for the user API.
"""

from django.urls import path
from user import views


app_name = "user"

urlpatterns = [
    path("create/", views.CreateUserView.as_view(), name="create"),
    path("login/", views.LogInView.as_view(), name="login"),
    path("logout/", views.LogOutView.as_view(), name="logout"),
    path("me/", views.ManageUserView.as_view(), name="me"),
]
