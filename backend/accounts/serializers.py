from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from fields import ModelSerializePrimaryKeyRelatedField
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField, EmailField, ImageField, IntegerField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from serializers import QueryStringValidateMixin

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


class UserRetrieveSerializer(ModelSerializer):
    # Receives user_id from url and JWT from request header -> no need to receive any fields from payload
    class Meta:
        model = User
        fields = USER_INFO_FIELDS
        read_only_fields = fields


class UserListSerializer(QueryStringValidateMixin, ModelSerializer):
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


class FollowUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "avatar"]
        read_only_fields = fields


class UserFollowingsRetrieveAndUpdateSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "followings", "followers"]
        read_only_fields = ["username"]

    followings = ModelSerializePrimaryKeyRelatedField(
        many=True,
        required=False,
        queryset=User.objects.all(),
        model_serializer_class=FollowUserSerializer,
    )
    followers = FollowUserSerializer(many=True, read_only=True)

    def validate_followings(self, value: list[User]) -> list[User]:
        if isinstance(self.instance, User) and self.instance in value:
            raise ValidationError("User can't follow oneself.", code="no_self_follow")
        return value


class UserFollowingsPartialUpdateSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "followings", "followers", "following"]
        read_only_fields = ["username"]

    followings = FollowUserSerializer(many=True, read_only=True)
    followers = FollowUserSerializer(many=True, read_only=True)

    following = PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)

    def validate_following(self, value: User) -> User:
        if isinstance(self.instance, User) and self.instance == value:
            raise ValidationError("User can't follow oneself.", code="no_self_follow")
        return value

    def update(self, instance: User, validated_data: dict[str, User]) -> User:
        instance.followings.add(validated_data.pop("following"))
        return instance
