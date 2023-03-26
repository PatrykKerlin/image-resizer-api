"""
Helper functions.
"""

from io import BytesIO

from django.conf import settings
from django.core.files import File

from rest_framework import status
from rest_framework.response import Response

import PIL.Image

from core.utils import constants
from core.models import Resized


def set_cookies(response, access_val, refresh_val):
    """Helper function for setting httponly cookies."""
    response.set_cookie(
        key=constants.ACCESS_TOKEN,
        value=access_val,
        httponly=True,
        expires=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
        max_age=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
    )
    response.set_cookie(
        key=constants.REFRESH_TOKEN,
        value=refresh_val,
        httponly=True,
        expires=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
        max_age=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
    )


def delete_cookies(response):
    """Helper function for deleting httponly cookies."""

    response.delete_cookie(constants.ACCESS_TOKEN)
    response.delete_cookie(constants.REFRESH_TOKEN)

    return response


def validate_new_size(parameters):
    if not (parameters["percent"] or parameters["width"] or parameters["height"]):
        return Response(
            {"error": "A new size must be specified."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if (parameters["percent"] and parameters["width"]) or (
        parameters["percent"] and parameters["height"]
    ):
        return Response(
            {"error": "Either the percentage or the new size must be given, not both."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    value_error_response = Response(
        {"error": "All given paramaters must be of type int."},
        status=status.HTTP_400_BAD_REQUEST,
    )

    if not parameters["quality"].isdigit():
        return value_error_response

    if parameters["percent"]:
        if not parameters["percent"].isdigit():
            return value_error_response

    if parameters["width"]:
        if not parameters["width"].isdigit():
            return value_error_response

    if parameters["height"]:
        if not parameters["height"].isdigit():
            return value_error_response

    return


def cast_new_size(parameters):
    if parameters["quality"]:
        parameters["quality"] = int(parameters["quality"])
        if parameters["quality"] < 1 or parameters["quality"] > 100:
            return Response(
                {"error": "Quality must be between 1 and 100."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    if parameters["percent"]:
        parameters["percent"] = int(parameters["percent"])
        if parameters["percent"] < 1:
            return Response(
                {"error": "Percent must be greater or equal to 1."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    if parameters["width"]:
        parameters["width"] = int(parameters["width"])
        if parameters["width"] < 1:
            return Response(
                {"error": "Width must be greater or equal to 1."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    if parameters["height"]:
        parameters["height"] = int(parameters["height"])
        if parameters["height"] < 1:
            return Response(
                {"error": "Height must be greater or equal to 1."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    return parameters


def resize_image(
    image,
    quality,
    proper_quality,
    new_width,
    new_height,
    format,
    user_obj,
    image_obj=None,
):
    img = PIL.Image.open(image)
    img_resized = img.resize((new_width, new_height))
    temp_img = BytesIO()
    img_resized.save(temp_img, format=format, quality=proper_quality)
    img_resized.seek(0)
    resized = Resized()
    resized.user = user_obj
    resized.quality = quality
    if image_obj:
        resized.image = image_obj
    resized.width = new_width
    resized.height = new_height
    resized.size = temp_img.tell()
    resized.resized_image.save(image.name, File(temp_img))
    resized.save()
    img_resized.close()
    temp_img.flush()

    return resized
