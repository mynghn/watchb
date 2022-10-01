from __future__ import annotations

from typing import Optional

from abstract_models import OnOffModel
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import MinLengthValidator
from django.db import models


class UserManager(UserManager):
    def create_user(
        self,
        email: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        **extra_fields,
    ) -> User:
        return super().create_user(username, email, password, **extra_fields)

    def create(self, *args, **kwargs) -> User:
        return self.create_user(*args, **kwargs)


class User(AbstractUser):
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]  # only for createsuperuser command

    username = models.CharField(
        max_length=150,
        help_text="Required. 2 to 150 characters. Letters, digits and @/./+/-/_ only.",
        validators=[MinLengthValidator(limit_value=2), AbstractUser.username_validator],
    )
    email = models.EmailField(unique=True)

    profile = models.TextField(blank=True)
    avatar = models.ImageField(blank=True, upload_to="accounts/avatar/%Y/%m/%d")
    background = models.ImageField(blank=True, upload_to="accounts/background/%Y/%m/%d")

    PUBLIC_OPTION = ("public", "전체공개")
    PRIVATE_OPTION = ("private", "친구공개")
    CLOSED_OPTION = ("closed", "비공개")
    VISIBILITY_CHOICES = [PUBLIC_OPTION, PRIVATE_OPTION, CLOSED_OPTION]
    visibility = models.CharField(
        max_length=7, choices=VISIBILITY_CHOICES, default=PUBLIC_OPTION[0]
    )

    objects = UserManager()


class Follow(OnOffModel):
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followings"
    )
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followers"
    )
