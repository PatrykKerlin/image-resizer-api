"""
Views for the user API.
"""

from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.parsers import FormParser
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication

from user.serializers import UserSerializer, TokenObtainPairSerializer

from core.utils.functions import set_cookies, delete_cookies

from drf_spectacular.utils import extend_schema


@extend_schema(tags=["user"])
class CreateUserView(CreateAPIView):
    """Create a new user view."""

    serializer_class = UserSerializer
    parser_classes = [FormParser]


@extend_schema(tags=["user"])
class ManageUserView(RetrieveUpdateDestroyAPIView):
    """Manage the authenticated user."""

    serializer_class = UserSerializer
    parser_classes = [FormParser]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    allowed_methods = ["GET", "PATCH", "DELETE"]

    def get_object(self):
        """Retrieve and return the authenticated user."""

        return self.request.user

    def delete(self, request, *args, **kwargs):
        """Delete the authenticated user."""

        response = super().delete(request, *args, **kwargs)
        return delete_cookies(response)


@extend_schema(tags=["authentication"])
class LogInView(TokenObtainPairView):
    """Create httponly cookies with jwt tokens for a user."""

    serializer_class = TokenObtainPairSerializer
    parser_classes = [FormParser]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        access = response.data.get("access", None)
        refresh = response.data.get("refresh", None)

        if response.status_code != status.HTTP_200_OK or not (access and refresh):
            return Response(
                {"success": False},
                status=status.HTTP_400_BAD_REQUEST,
            )

        set_cookies(response, access, refresh)

        response.data["success"] = True

        return response


@extend_schema(tags=["authentication"])
class LogOutView(APIView):
    """Delete httponly cookies with jwt tokens."""

    serializer_class = None
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_204_NO_CONTENT)
        return delete_cookies(response)
