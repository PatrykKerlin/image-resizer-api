"""
Tests for the Django admin modifications.
"""

import tempfile
import PIL.Image

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status

from core.models import Tier, ThumbnailSize, Image, Thumbnail


class AdminSiteTests(TestCase):
    """Tests for Django admin."""

    def setUp(self):
        """Create user and client."""

        self.client = Client()
        self.superuser = get_user_model().objects.create_superuser(
            username="admin",
            password="test1234",
        )
        self.client.force_login(self.superuser)
        self.tier = Tier.objects.create(name="test")
        self.thumb = ThumbnailSize.objects.create(tier=self.tier, height=200)
        self.user = get_user_model().objects.create_user(
            username="user",
            password="test1234",
            tier=self.tier,
        )

    # Users page
    def test_users_list(self):
        """Test that users are listed on page."""

        url = reverse("admin:core_user_changelist")
        response = self.client.get(url)

        self.assertContains(response, self.user.username)

    def test_edit_user_page(self):
        """Test the edit user page works."""

        url = reverse("admin:core_user_change", args=[self.user.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_user_page(self):
        """Test the create user page works."""

        url = reverse("admin:core_user_add")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Tiers page
    def test_tiers_list(self):
        """Test that tiers are listed on page."""

        url = reverse("admin:core_tier_changelist")
        response = self.client.get(url)

        self.assertContains(response, self.tier.name)

    def test_edit_tier_page(self):
        """Test the edit tier page works."""

        url = reverse("admin:core_tier_change", args=[self.tier.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_tier_page(self):
        """Test the create tier page works."""

        url = reverse("admin:core_tier_add")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Thumbnail sizes page
    def test_thumbnail_sizes_list(self):
        """Test that thumbnail sizes are listed on page."""

        url = reverse("admin:core_thumbnailsize_changelist")
        response = self.client.get(url)

        self.assertContains(response, self.thumb.height)

    def test_edit_thumbnail_sizes_page(self):
        """Test the edit thumbnail sizes page works."""

        url = reverse("admin:core_thumbnailsize_change", args=[self.thumb.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_thumbnail_size_page(self):
        """Test the create thumbnail size page works."""

        url = reverse("admin:core_thumbnailsize_add")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AdminImageSiteTests(TestCase):
    """Tests for Django admin."""

    def setUp(self):
        """Create and return a user and a client."""

        self.client = Client()
        self.superuser = get_user_model().objects.create_superuser(
            username="admin",
            password="test1234",
        )
        self.client.force_login(self.superuser)
        self.tier = Tier.objects.create(name="test")
        self.thumb = ThumbnailSize.objects.create(tier=self.tier, height=200)
        self.user = get_user_model().objects.create_user(
            username="user",
            password="test1234",
            tier=self.tier,
        )
        with tempfile.NamedTemporaryFile(suffix=".jpg") as image_file:
            img = PIL.Image.new("RGB", (10, 10))
            img.save(image_file, format="JPEG")
            image_file.seek(0)
            image = Image(user=self.user)
            image.image.save("temp_filename.jpg", image_file)

    def tearDown(self):
        """Clean up after test."""

        if Image.objects.filter(user=self.user).exists():
            Image.objects.get(user=self.user).delete()
        while Thumbnail.objects.filter(user=self.user).exists():
            Thumbnail.objects.filter(user=self.user).first().delete()

    # Images page
    def test_images_list(self):
        """Test that images are listed on page."""

        url = reverse("admin:core_image_changelist")
        response = self.client.get(url)

        self.assertContains(response, Image.objects.get(user=self.user).id)

    def test_edit_images_page(self):
        """Test the edit images page works."""

        url = reverse(
            "admin:core_image_change", args=[Image.objects.get(user=self.user).id]
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_image_page(self):
        """Test the create image size page works."""

        url = reverse("admin:core_image_add")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Thumbnails page
    def test_thumbnails_list(self):
        """Test that thumbnails are listed on page."""

        url = reverse("admin:core_thumbnail_changelist")
        response = self.client.get(url)

        self.assertContains(response, Thumbnail.objects.get(user=self.user).id)

    def test_edit_thumbnails_page(self):
        """Test the edit thumbnails page works."""

        url = reverse(
            "admin:core_thumbnail_change",
            args=[Thumbnail.objects.get(user=self.user).id],
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_thumbnail_page(self):
        """Test the create thumbnail size page works."""

        url = reverse("admin:core_thumbnail_add")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
