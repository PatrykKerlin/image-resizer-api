# import time
# import base64
# from binascii import Error

# from django.shortcuts import redirect
# from django.http import Http404
from django.contrib.auth import get_user_model
from core.models import User

from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, TokenError

from core.utils.functions import set_cookies, delete_cookies
from core.utils import constants


class JWTMiddleware:
    """Middleware for checking, validating and updating jwt tokens
    in httponly cookies."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        access_token = request.COOKIES.get(constants.ACCESS_TOKEN, None)
        refresh_token = request.COOKIES.get(constants.REFRESH_TOKEN, None)

        if not access_token and not refresh_token:
            return response

        if not access_token:
            return delete_cookies(response)

        try:
            access_token_decoded = AccessToken(access_token)
            user = get_user_model().objects.get(
                id=access_token_decoded.payload.get("user_id")
            )
            request.META["HTTP_AUTHORIZATION"] = f"Bearer {access_token_decoded}"
            auth_response = self.get_response(request)

            return auth_response

        except TokenError:
            if not refresh_token:
                return delete_cookies(response)

            try:
                decoded_refresh_token = RefreshToken(refresh_token)

                user = get_user_model().objects.get(
                    id=decoded_refresh_token.payload.get("user_id")
                )
                user_id = user.id
                refresh_token = RefreshToken()
                access_token = AccessToken()
                access_token.payload["user_id"] = user_id
                refresh_token.payload["user_id"] = user_id

                request.META["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"

                auth_response = self.get_response(request)

                set_cookies(auth_response, access_token, refresh_token)

                return auth_response

            except TokenError:
                return delete_cookies(response)
        except User.DoesNotExist:
            return delete_cookies(response)


# class ExpiringLinkMiddleware:
#     """Middleware for handling expiring links."""

#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         if request.GET.get("exp") == "1":
#             if link := self.decode_link(request):
#                 return redirect(link)
#             raise Http404("Invalid or expired link.")

#         response = self.get_response(request)
#         return response

#     def decode_link(self, request):
#         """URL decoding method."""
#         try:
#             decrypted_path = base64.urlsafe_b64decode(
#                 request.path[1:].encode("utf-8")
#             ).decode("utf-8")
#             expire_time_str = decrypted_path.split("=")[-1]
#             expire_time = int(expire_time_str)
#             if expire_time < time.time():
#                 return False
#             return decrypted_path.split("?")[0]
#         except (UnicodeDecodeError, Error, ValueError):
#             return False
