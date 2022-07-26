from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "password", "id", "date_joined"]
        read_only_fields = ["id", "date_joined"]
        extra_kwargs = {"password": {"write_only": True}}


USER_INFO_FIELDS = (
    "id",
    "email",
    "username",
    "profile",
    "visibility",
    "is_active",
    "is_staff",
    "is_superuser",
    "date_joined",
    "last_login",
    "avatar",
    "background",
)


class UserRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = USER_INFO_FIELDS
        read_only_fields = USER_INFO_FIELDS
