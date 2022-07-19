from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from django.db import models


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
    avatar = models.ImageField(blank=True, upload_to="account/avatar/%Y/%m/%d")
    background = models.ImageField(blank=True, upload_to="account/background/%Y/%m/%d")

    PUBLIC_OPTION = ("public", "전체공개")
    PRIVATE_OPTION = ("private", "친구공개")
    CLOSED_OPTION = ("closed", "비공개")
    VISIBILITY_CHOICES = [PUBLIC_OPTION, PRIVATE_OPTION, CLOSED_OPTION]
    visibility = models.CharField(
        max_length=7, choices=VISIBILITY_CHOICES, default=PUBLIC_OPTION[0]
    )
