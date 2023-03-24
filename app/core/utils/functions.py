"""
Helper functions.
"""

from django.conf import settings
from core.utils import constants


def set_cookies(response, access_val, refresh_val):
    """Helper function for setting httponly cookies."""
    response.set_cookie(
        key=constants.ACCESS_TOKEN,
        value=access_val,
        httponly=True,
        expires=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
        max_age=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
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
