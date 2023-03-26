"""
Tests for the image API.
"""

import os
import tempfile

from PIL import Image

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core import models


IMAGE_URL = reverse("image:image-list")
THUMBNAIL_URL = reverse("image:thumbnail-list")


def image_detail_url(id):
    """Create and return a image detail URL."""

    return reverse("image:image-detail", args=[id])


def thumbnail_detail_url(id):
    """Create and return a thumbnail detail URL."""

    return reverse("image:thumbnail-detail", args=[id])


def expiring_link_detail_url(id):
    """Create and return an expiring link detail URL."""

    return reverse("image:link-detail", args=[id])


class PublicImageAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        """Create and return a user and a client."""
        self.client = APIClient()
        tier = models.Tier.objects.create(name="Test tier 2 thumbs")
        models.ThumbnailSize.objects.create(tier=tier, height=200)
        models.ThumbnailSize.objects.create(tier=tier, height=400)
        self.user = get_user_model().objects.create_user(
            username="test",
            password="test1234",
            tier=tier,
        )

    def tearDown(self):
        """Clean up after test."""

        if models.Image.objects.filter(user=self.user).exists():
            models.Image.objects.get(user=self.user).delete()
        for thumb in models.Thumbnail.objects.filter(user=self.user):
            thumb.delete()

    def test_upload_image_unauthorized_user(self):
        """Test uploading an image by unauthorized user."""

        with tempfile.NamedTemporaryFile(suffix=".jpg") as image_file:
            img = Image.new("RGB", (10, 10))
            img.save(image_file, format="JPEG")
            image_file.seek(0)
            payload = {
                "image": image_file,
                "username": self.user.username,
            }
            response = self.client.post(IMAGE_URL, payload, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(models.Image.objects.count(), 0)


class PrivateImageAPITests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        """Create and return a user and a client."""
        self.client = APIClient()
        tier = models.Tier.objects.create(
            name="Test tier 2 thumbs",
            thumbnails=True,
            original_size=True,
            expiring_link=True,
        )
        models.ThumbnailSize.objects.create(tier=tier, height=200)
        models.ThumbnailSize.objects.create(tier=tier, height=400)
        self.user = get_user_model().objects.create_user(
            username="test",
            password="test1234",
            tier=tier,
        )
        self.client.force_authenticate(self.user)

        image_file = tempfile.NamedTemporaryFile(suffix=".jpg")
        img = Image.new("RGB", (10, 10))
        img.save(image_file, format="JPEG")
        image_file.seek(0)
        self.payload = {
            "image": image_file,
            "username": self.user.username,
        }

    def tearDown(self):
        """Clean up after test."""

        if models.Image.objects.filter(user=self.user).exists():
            models.Image.objects.get(user=self.user).delete()
        while models.Thumbnail.objects.filter(user=self.user).exists():
            models.Thumbnail.objects.filter(user=self.user).first().delete()

    def test_upload_image_authorized_user(self):
        """Test uploading an image by authorized user."""

        response = self.client.post(IMAGE_URL, self.payload, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            os.path.exists(models.Image.objects.get(user=self.user).image.path)
        )

    def test_upload_image_bad_request(self):
        """Test uploading invalid image."""

        payload = {
            "image": "not_an_image",
            "username": self.user.username,
        }
        response = self.client.post(IMAGE_URL, payload, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_images(self):
        """Test list of uploaded images."""

        self.client.post(IMAGE_URL, self.payload, format="multipart")

        response = self.client.get(IMAGE_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            os.path.exists(models.Image.objects.get(user=self.user).image.path)
        )

    def test_image_details(self):
        """Test detail view of uploaded images."""

        self.client.post(IMAGE_URL, self.payload, format="multipart")

        id = models.Image.objects.get(user=self.user).id
        url = image_detail_url(id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], id)
        self.assertTrue(response.data["image"])

    def test_image_delete(self):
        """Test deleting uploaded image."""

        self.client.post(IMAGE_URL, self.payload, format="multipart")

        id = models.Image.objects.get(user=self.user).id
        url = image_detail_url(id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(models.Image.objects.filter(user=self.user).exists())
        self.assertEqual(models.Image.objects.count(), 0)
        self.assertFalse(models.Thumbnail.objects.filter(user=self.user).exists())
        self.assertEqual(models.Thumbnail.objects.count(), 0)

    def test_creating_thumbnails(self):
        """Test creating thumbnails for uploaded image."""

        self.client.post(IMAGE_URL, self.payload, format="multipart")

        response = self.client.get(IMAGE_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.Thumbnail.objects.count(), 2)

    def test_list_thumbnails(self):
        """Test list of generated thumbnails."""

        self.client.post(IMAGE_URL, self.payload, format="multipart")

        response = self.client.get(THUMBNAIL_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_thumbnail_details(self):
        """Test detail view of generated thumbnails."""

        self.client.post(IMAGE_URL, self.payload, format="multipart")

        thumb = models.Thumbnail.objects.filter(user=self.user).first()
        url = thumbnail_detail_url(thumb.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], thumb.id)
        self.assertTrue(response.data["thumbnail"])

    def test_thumbnail_delete(self):
        """Test deleting generated thumbnail."""

        self.client.post(IMAGE_URL, self.payload, format="multipart")

        thumb = models.Thumbnail.objects.filter(user=self.user).first()
        url = thumbnail_detail_url(thumb.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(models.Thumbnail.objects.filter(id=thumb.id).exists())
        self.assertEqual(models.Thumbnail.objects.count(), 1)

    def test_generating_expiring_link(self):
        """Test generating expiring links."""

        self.client.post(IMAGE_URL, self.payload, format="multipart")

        id = models.Image.objects.get(user=self.user).id
        url = expiring_link_detail_url(id)
        url = f"{url}?time=500"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("url", response.data)
