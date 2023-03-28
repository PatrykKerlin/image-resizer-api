"""
Views for the image API.
"""

import time
import base64

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from rest_framework import status, generics, viewsets, mixins
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

import PIL.Image

from core.models import Image, Resized
from . import serializers
from core.utils.functions import validate_new_size, cast_new_size, resize_image


@extend_schema(tags=["images"])
class DetailImageAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Image.objects.all()
    serializer_class = serializers.UpdateImageSerializer
    parser_classes = [MultiPartParser, FormParser]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    allowed_methods = ["GET", "PATCH", "DELETE"]

    def get_queryset(self):
        return Image.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        print(self)
        if self.request.method == "GET":
            return serializers.DetailImageSerializer
        return self.serializer_class


@extend_schema(tags=["images"])
class ImageAPIView(generics.ListCreateAPIView):
    queryset = Image.objects.all()
    serializer_class = serializers.ListImageSerializer
    parser_classes = [MultiPartParser, FormParser]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    allowed_methods = ["GET", "POST"]

    def get_queryset(self):
        return Image.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        print(self)
        if self.request.method == "POST":
            return serializers.CreateImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.validated_data["name"] = serializer.validated_data["image"].name
        serializer.validated_data["size"] = serializer.validated_data["image"].size
        img = PIL.Image.open(serializer.validated_data["image"])
        (
            serializer.validated_data["width"],
            serializer.validated_data["height"],
        ) = img.size
        serializer.validated_data["format"] = img.format
        serializer.save(user=self.request.user)
        img.close()

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({"id": response.data["id"]}, response.status_code)


@extend_schema(
    tags=["images"],
    parameters=[
        OpenApiParameter(
            name="quality",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
        ),
        OpenApiParameter(
            name="percent",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
        ),
        OpenApiParameter(
            name="width",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
        ),
        OpenApiParameter(
            name="height",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
        ),
    ],
)
class CreateImageResizedAPIView(generics.CreateAPIView):
    queryset = Image.objects.all()
    serializer_class = serializers.CreateImageSerializer
    parser_classes = [MultiPartParser, FormParser]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    allowed_methods = ["POST"]

    def get_queryset(self):
        return Image.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        parameters = {}
        parameters["quality"] = self.request.query_params.get("quality", "75")
        parameters["percent"] = self.request.query_params.get("percent", None)
        parameters["width"] = self.request.query_params.get("width", None)
        parameters["height"] = self.request.query_params.get("height", None)

        error_response = validate_new_size(parameters)
        if error_response:
            return error_response

        int_parameters = cast_new_size(parameters)
        if isinstance(int_parameters, Response):
            return int_parameters

        serializer.validated_data["name"] = serializer.validated_data["image"].name
        serializer.validated_data["size"] = serializer.validated_data["image"].size
        img = PIL.Image.open(serializer.validated_data["image"])
        (
            serializer.validated_data["width"],
            serializer.validated_data["height"],
        ) = img.size
        serializer.validated_data["format"] = img.format
        serializer.save(user=self.request.user)

        if int_parameters["quality"] > 95:
            proper_quality = 95
        else:
            proper_quality = int_parameters["quality"]

        if int_parameters["percent"]:
            new_width = int(
                serializer.validated_data["width"] * (int_parameters["percent"] / 100)
            )
            new_height = int(
                serializer.validated_data["height"] * (int_parameters["percent"] / 100)
            )

        if int_parameters["width"] and not int_parameters["height"]:
            new_width = int(int_parameters["width"])
            new_height = int(
                serializer.validated_data["height"]
                * (new_width / serializer.validated_data["width"])
            )

        if int_parameters["height"] and not int_parameters["width"]:
            new_height = int(int_parameters["height"])
            new_width = int(
                serializer.validated_data["width"]
                * (new_height / serializer.validated_data["height"])
            )

        if int_parameters["width"] and int_parameters["height"]:
            new_width = int(int_parameters["width"])
            new_height = int(int_parameters["height"])

        resized = resize_image(
            serializer.validated_data["image"],
            int_parameters["quality"],
            proper_quality,
            new_width,
            new_height,
            serializer.validated_data["format"],
            self.request.user,
        )

        self.resized_id = resized.id

        img.close()

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        resized_image = Resized.objects.get(id=self.resized_id)
        resized_image.image = Image.objects.get(id=response.data["id"])
        resized_image.save()

        host = f"http://{request.META['HTTP_HOST']}/static/media/"
        response.data["name"] = resized_image.image.name
        response.data["resized_id"] = resized_image.id
        response.data["resized_image"] = f"{host}{resized_image.resized_image.name}"

        return response


@extend_schema(tags=["images"])
class GetResizedAPIView(APIView):
    serializer_class = serializers.DetailResizedSerializer
    parser_classes = [MultiPartParser, FormParser]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="quality",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                name="percent",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                name="width",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                name="height",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
            ),
        ]
    )
    def get(self, request, pk):
        try:
            parameters = {}
            parameters["quality"] = self.request.query_params.get("quality", "75")
            parameters["percent"] = self.request.query_params.get("percent", None)
            parameters["width"] = self.request.query_params.get("width", None)
            parameters["height"] = self.request.query_params.get("height", None)

            error_response = validate_new_size(parameters)
            if error_response:
                return error_response

            int_parameters = cast_new_size(parameters)
            if isinstance(int_parameters, Response):
                return int_parameters

            image = Image.objects.get(id=pk)

            if int_parameters["quality"] > 95:
                proper_quality = 95
            else:
                proper_quality = int_parameters["quality"]

            if int_parameters["percent"]:
                new_width = int(image.width * (int_parameters["percent"] / 100))
                new_height = int(image.height * (int_parameters["percent"] / 100))

            if int_parameters["width"] and not int_parameters["height"]:
                new_width = int(int_parameters["width"])
                new_height = int(image.height * (new_width / image.width))

            if int_parameters["height"] and not int_parameters["width"]:
                new_height = int(int_parameters["height"])
                new_width = int(image.width * (new_height / image.height))

            if int_parameters["width"] and int_parameters["height"]:
                new_width = int(int_parameters["width"])
                new_height = int(int_parameters["height"])

            resized = resize_image(
                image.image,
                int_parameters["quality"],
                proper_quality,
                new_width,
                new_height,
                image.format,
                image.user,
                image,
            )

        except Image.DoesNotExist:
            return Response(
                {"error": "Image does not exist."}, status=status.HTTP_404_NOT_FOUND
            )
        host = f"http://{request.META['HTTP_HOST']}/static/media/"
        return Response(
            {
                "id": resized.id,
                "resized_image": f"{host}{resized.resized_image.name}",
            }
        )


@extend_schema(tags=["resized_images"])
class DetailResizedAPIView(generics.RetrieveDestroyAPIView):
    queryset = Resized.objects.all()
    serializer_class = serializers.DetailResizedSerializer
    parser_classes = [FormParser]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    allowed_methods = ["GET", "DELETE"]

    def get_queryset(self):
        return Resized.objects.filter(user=self.request.user)


@extend_schema(tags=["resized_images"])
class ResizedAPIView(generics.ListAPIView):
    queryset = Resized.objects.all()
    serializer_class = serializers.ListResizedSerializer
    parser_classes = [FormParser]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    allowed_methods = ["GET"]

    def get_queryset(self):
        return Resized.objects.filter(user=self.request.user)


@extend_schema(tags=["expiring_links"])
@extend_schema_view(
    retrieve=extend_schema(
        parameters=[
            OpenApiParameter(
                "time",
                OpenApiTypes.INT,
                required=True,
            ),
        ]
    )
)
class LinkViewSet(
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """View for managing expiring_links."""

    serializer_class = serializers.LinkSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        self.model = self.request.path.split("/")[3]
        if self.model == "resized":
            return Resized.objects.filter(user=self.request.user)
        return Image.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """A method generating expiring links."""

        if not self.get_object():
            return Response(
                {"error": "Image does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

        request_time = self.request.query_params.get("time", None)

        if not request_time:
            return Response(
                {"error": "Expiring time must be provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        image = self.get_object()

        if not request_time.isdigit():
            {"error": "Expiring time must be of type int."},
            return Response(status=status.HTTP_400_BAD_REQUEST)

        request_time_int = int(request_time)

        if request_time_int < 1:
            return Response(
                {"error": "Given expiring time must be positive."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        exp_time = int(time.time()) + (request_time_int * 60)

        if self.model == "resized":
            url_with_exp = f"{image.resized_image.url}?expires={exp_time}"
        else:
            url_with_exp = f"{image.image.url}?expires={exp_time}"
        # URL encoding to hide the original path and expiration time
        # Decoding takes place in the custom middleware
        encrypted_path = base64.urlsafe_b64encode(url_with_exp.encode("utf-8")).decode(
            "utf-8"
        )
        try:
            encrypted_url_with_exp = (
                f"http://{request.META['HTTP_HOST']}/{encrypted_path}?exp=1"
            )
        # Code snippet for testing purposes only
        except KeyError:
            encrypted_url_with_exp = f"http://example.com/{encrypted_path}?exp=1"

        return Response(
            {
                "url": encrypted_url_with_exp,
                "expires_in": request_time_int,
            },
            status=status.HTTP_200_OK,
        )
