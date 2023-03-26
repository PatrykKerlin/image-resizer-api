"""
Database models.
"""

import os
import uuid
import datetime

from django.db import models
from django.core.validators import (
    validate_image_file_extension,
    MinValueValidator,
    MaxValueValidator,
)
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


def image_file_path(instance, filename):
    """Generate file path for new image"""

    extension = os.path.splitext(filename)[1]
    user_id = instance.user.id
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
    unique_id = str(uuid.uuid4()).split("-")[-1]
    filename = f"{user_id}_{timestamp}_{unique_id}_{repr(instance)}{extension}"

    return os.path.join("uploads", "images", str(user_id), filename)


class UserManager(BaseUserManager):
    """Manager for users"""

    def create_user(self, email, name, password=None, **kwargs):
        """Create, save and return a new user."""

        if not email:
            raise ValueError("User must have an email address.")

        if not name:
            raise ValueError("User must have a name.")

        user = self.model(email=self.normalize_email(email), name=name, **kwargs)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, name, password):
        """Create, save and return a new superuser."""

        user = self.create_user(email, name, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    User model.
    """

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return self.name


class Image(models.Model):
    """Image model."""

    user = models.ForeignKey("User", on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to=image_file_path, validators=[validate_image_file_extension]
    )
    name = models.TextField(max_length=255)
    width = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    height = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    format = models.TextField(max_length=4)
    size = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    description = models.TextField(max_length=255, null=True)

    def __str__(self):
        return f"{self.id}. {self.name}"

    def __repr__(self):
        return "original"

    def delete(self, *args, **kwargs):
        os.remove(self.image.path)
        return super(Image, self).delete(*args, **kwargs)


class Resized(models.Model):
    """Resized image model."""

    user = models.ForeignKey("User", on_delete=models.CASCADE)
    image = models.ForeignKey("Image", on_delete=models.CASCADE, null=True)
    resized_image = models.ImageField(
        upload_to=image_file_path, validators=[validate_image_file_extension]
    )
    quality = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    width = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    height = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    size = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return f"{self.id}. {self.image.name}"

    def __repr__(self):
        return "resized"

    def delete(self, *args, **kwargs):
        os.remove(self.resized_image.path)
        return super(Resized, self).delete(*args, **kwargs)
