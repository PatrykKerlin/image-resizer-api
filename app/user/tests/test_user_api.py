"""
Tests for the user API.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Tier


TOKEN_URL = reverse("user:token")
USERNAME = "test"
PASSWORD = "test1234"


def create_user(username=USERNAME, password=PASSWORD, **kwargs):
    """Create and return a new user."""

    tier = Tier.objects.create(name="test")

    return get_user_model().objects.create_user(username, password, tier, **kwargs)


class PublicUserAPITests(TestCase):
    """Test the public features of the user API."""

    def setUp(self):
        """Create user and client."""

        self.client = APIClient()
        create_user()

    def test_create_token_for_user(self):
        """Test generates token for valid credentials."""

        payload = {
            "username": USERNAME,
            "password": PASSWORD,
        }
        response = self.client.post(TOKEN_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_create_token_bad_username(self):
        """Test posting a bad username returns an error."""
        payload = {
            "username": "badname",
            "password": PASSWORD,
        }
        response = self.client.post(TOKEN_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", response.data)

    def test_create_token_bad_password(self):
        """Test posting a bad password returns an error."""

        payload = {
            "username": USERNAME,
            "password": "badpassword",
        }
        response = self.client.post(TOKEN_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", response.data)

    def test_create_token_blank_password(self):
        """Test posting a blank password returns an error."""

        payload = {
            "username": USERNAME,
            "password": "",
        }
        response = self.client.post(TOKEN_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", response.data)
