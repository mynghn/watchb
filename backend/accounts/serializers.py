from collections import OrderedDict
from typing import Any, Mapping

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField, EmailField, ImageField, IntegerField
from rest_framework.serializers import ModelSerializer
from rest_framework.settings import api_settings

from .validators import PasswordValidator

User = get_user_model()


class SignUpSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "password", "id", "date_joined"]
        read_only_fields = ["id", "date_joined"]

    password = CharField(
        write_only=True, max_length=128, validators=[PasswordValidator()]
    )


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


class UserUpdateSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = list(set(USER_INFO_FIELDS) - {"avatar", "background"}) + [
            "curr_password",
            "new_password",
        ]
        read_only_fields = ["id", "date_joined", "last_login"]

    curr_password = CharField(required=False, write_only=True, max_length=128)
    new_password = CharField(
        required=False,
        write_only=True,
        max_length=128,
        validators=[PasswordValidator()],
    )

    def validate_curr_password(self, value: str) -> str:
        assert isinstance(
            self.instance, User
        ), "Only update with existing user instance is supported"

        if not self.instance.check_password(value):
            raise ValidationError(
                "Please request with correct password", code="incorrect"
            )

        return value

    def validate(self, attrs: dict[str, Any]):
        validated_data = super().validate(attrs)
        if ("email" in validated_data.keys()) and (
            "curr_password" not in validated_data.keys()
        ):
            raise ValidationError(
                {"curr_password": "To update email, curr_password is needed"},
                code="required",
            )
        elif (new_provided := ("new_password" in validated_data.keys())) and (
            "curr_password" not in validated_data.keys()
        ):
            raise ValidationError(
                {
                    "curr_password": "To update password, both curr_password & new_password are needed"
                },
                code="required",
            )
        elif new_provided:
            if validated_data["new_password"] == validated_data["curr_password"]:
                raise ValidationError(
                    {"new_password": "New password should be different from old one."},
                    code="invalid",
                )
        return validated_data

    def update(self, instance: User, validated_data: dict[str, Any]):
        if "new_password" in validated_data.keys():
            instance.password = make_password(validated_data.pop("new_password"))
        validated_data.pop("curr_password", None)
        return super().update(instance, validated_data)


class UserAvatarUpdateSerializer(ModelSerializer):
    class Meta:
        model = User
        read_only_fields = ["id", "username"]
        fields = read_only_fields + ["avatar"]

    avatar = ImageField(max_length=100)


class UserBackgroundUpdateSerializer(ModelSerializer):
    class Meta:
        model = User
        read_only_fields = ["id", "username"]
        fields = read_only_fields + ["background"]

    background = ImageField(max_length=100)


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
