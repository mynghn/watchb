from collections import OrderedDict
from typing import Mapping

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
from rest_framework.fields import EmailField, IntegerField
from rest_framework.serializers import ModelSerializer
from rest_framework.settings import api_settings

User = get_user_model()


class SignUpSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "password", "id", "date_joined"]
        read_only_fields = ["id", "date_joined"]
        extra_kwargs = {"password": {"write_only": True}}


USER_INFO_FIELDS = [
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
]


class UserDetailSerializer(ModelSerializer):
    # Receives user_id from url and JWT from request header -> no need to receive any fields from payload
    class Meta:
        model = User
        fields = USER_INFO_FIELDS
        read_only_fields = USER_INFO_FIELDS


class UserListSerializer(ModelSerializer):
    default_error_messages = {
        **ModelSerializer.default_error_messages,
        "undefined": _(
            "Query key not allowed. Expected one of {valid_keys}, but got {invalid_keys}."
        ),
    }

    id = IntegerField(label="ID", required=False)
    email = EmailField(max_length=254, required=False)

    class Meta:
        model = User
        fields = USER_INFO_FIELDS
        read_only_fields = [
            "profile",
            "date_joined",
            "last_login",
            "avatar",
            "background",
        ]  # non exact searchable fields
        extra_kwargs = {"email": {"required": False}, "username": {"required": False}}

    def validate_query_string(self, query_params: Mapping):
        if isinstance(query_params, Mapping):
            defined_query_keys = {
                fname for fname, field in self.fields.items() if not field.read_only
            }
            unexpected_query_keys = [
                qkey for qkey in query_params.keys() if qkey not in defined_query_keys
            ]
            if unexpected_query_keys:
                message = self.error_messages["undefined"].format(
                    valid_keys=defined_query_keys, invalid_keys=unexpected_query_keys
                )
                raise ValidationError(
                    {api_settings.NON_FIELD_ERRORS_KEY: [message]}, code="undefined"
                )

    def to_internal_value(self, data: Mapping) -> OrderedDict:
        self.validate_query_string(query_params=data)
        return super().to_internal_value(data)
