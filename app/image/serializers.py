"""
Serilizers for image API.
"""

from rest_framework import serializers
from core.models import Image, Resized

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field


class CreateImageSerializer(serializers.ModelSerializer):
    """Serializer for creating images."""

    class Meta:
        model = Image
        fields = ["id", "image", "description"]
        read_only_fields = ["id"]
        extra_kwargs = {"image": {"required": True}}


class ListImageSerializer(serializers.ModelSerializer):
    """Serializer for viewing images details."""

    class Meta:
        model = Image
        fields = ["id", "name", "description"]
        read_only_fields = ["id"]


class DetailImageSerializer(serializers.ModelSerializer):
    """Serializer for viewing images details."""

    owner = serializers.SerializerMethodField()
    resolution = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = [
            "id",
            "owner",
            "image",
            "name",
            "resolution",
            "format",
            "size",
            "description",
        ]
        read_only_fields = ["id"]

    @extend_schema_field(OpenApiTypes.STR)
    def get_owner(self, obj):
        return obj.user.name

    @extend_schema_field(OpenApiTypes.STR)
    def get_resolution(self, obj):
        return f"{obj.width}x{obj.height}px"

    @extend_schema_field(OpenApiTypes.STR)
    def get_size(self, obj):
        if obj.size / 1048576 >= 1:
            return f"{round(obj.size / 1048576, 2)}MB"
        return f"{round(obj.size/1024, 2)}KB"


class UpdateImageSerializer(serializers.ModelSerializer):
    """Serializer for viewing images details."""

    class Meta:
        model = Image
        fields = ["id", "description"]
        read_only_fields = ["id"]


class ListResizedSerializer(serializers.ModelSerializer):
    """Serializer for thumbnails."""

    name = serializers.SerializerMethodField()
    resolution = serializers.SerializerMethodField()

    class Meta:
        model = Resized
        fields = ["id", "name", "resolution"]
        read_only_fields = ["id"]

    @extend_schema_field(OpenApiTypes.STR)
    def get_name(self, obj):
        return obj.image.name

    @extend_schema_field(OpenApiTypes.STR)
    def get_resolution(self, obj):
        return f"{obj.width}x{obj.height}px"


class DetailResizedSerializer(serializers.ModelSerializer):
    """Serializer for viewing images details."""

    image_id = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    resolution = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    format = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = Resized
        fields = [
            "id",
            "image_id",
            "owner",
            "resized_image",
            "name",
            "resolution",
            "format",
            "size",
            "description",
        ]
        read_only_fields = ["id"]

    @extend_schema_field(OpenApiTypes.STR)
    def get_image_id(self, obj):
        return obj.image.id

    @extend_schema_field(OpenApiTypes.STR)
    def get_name(self, obj):
        return obj.image.name

    @extend_schema_field(OpenApiTypes.STR)
    def get_format(self, obj):
        return obj.image.format

    @extend_schema_field(OpenApiTypes.STR)
    def get_owner(self, obj):
        return obj.user.name

    @extend_schema_field(OpenApiTypes.STR)
    def get_resolution(self, obj):
        return f"{obj.width}x{obj.height}px"

    @extend_schema_field(OpenApiTypes.STR)
    def get_size(self, obj):
        if obj.size / 1048576 >= 1:
            return f"{round(obj.size / 1048576, 2)}MB"
        return f"{round(obj.size/1024, 2)}KB"

    @extend_schema_field(OpenApiTypes.STR)
    def get_description(self, obj):
        return obj.image.description


class LinkSerializer(serializers.ModelSerializer):
    """Serializer for generating links."""

    time = serializers.IntegerField()

    class Meta:
        model = Image
        fields = ["id", "time"]
        read_only_fields = ["id"]
        extra_kwargs = {"time": {"required": True}}
