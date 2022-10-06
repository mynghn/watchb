from collections import OrderedDict
from typing import Mapping

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
from rest_framework.fields import ChoiceField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer
from rest_framework.settings import api_settings

from serializers import UseIndexedListSerializerMixin

from .models import (
    Blocklist,
    Country,
    Credit,
    Genre,
    Movie,
    Person,
    Poster,
    Rating,
    Review,
    Still,
    Video,
    Wishlist,
)


class CountryRetrieveSerializer(ModelSerializer):
    class Meta:
        model = Country
        fields = ["alpha_2", "name"]
        read_only_fields = fields


class GenreRetrieveSerializer(ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name"]
        read_only_fields = fields


class PersonRetrieveSerializer(ModelSerializer):
    class Meta:
        model = Person
        fields = ["id", "name", "avatar_url", "biography"]
        read_only_fields = fields


class CreditRetrieveSerializer(ModelSerializer):
    class Meta:
        model = Credit
        fields = ["id", "job", "cameo_type", "role_name", "person"]
        read_only_fields = fields

    person = PersonRetrieveSerializer()


class PosterRetrieveSerializer(ModelSerializer):
    class Meta:
        model = Poster
        fields = ["id", "image_url", "is_main"]
        read_only_fields = fields


class StillRetrieveSerializer(ModelSerializer):
    class Meta:
        model = Still
        fields = ["id", "image_url"]
        read_only_fields = fields


class VideoRetrieveSerializer(ModelSerializer):
    class Meta:
        model = Video
        fields = ["id", "title", "site", "external_id"]
        read_only_fields = fields


class MovieRetrieveSerializer(ModelSerializer):
    class Meta:
        model = Movie
        fields = [
            "id",
            "title",
            "release_date",
            "production_year",
            "running_time",
            "synopsys",
            "film_rating",
            "countries",
            "genres",
            "credits",
            "poster_set",
            "still_set",
            "video_set",
        ]
        read_only_fields = fields

    countries = CountryRetrieveSerializer(many=True)
    genres = GenreRetrieveSerializer(many=True)
    credits = CreditRetrieveSerializer(many=True)
    poster_set = PosterRetrieveSerializer(many=True)
    still_set = StillRetrieveSerializer(many=True)
    video_set = VideoRetrieveSerializer(many=True)


class RatingCreateSerializer(ModelSerializer):
    class Meta:
        model = Rating
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class RatingUpdateSerializer(ModelSerializer):
    class Meta(RatingCreateSerializer.Meta):
        read_only_fields = [
            "user",
            "movie",
        ] + RatingCreateSerializer.Meta.read_only_fields


User = get_user_model()


class RatingListSerializer(UseIndexedListSerializerMixin, ModelSerializer):
    default_error_messages = {
        **ModelSerializer.default_error_messages,
        "undefined": _(
            "Query key not allowed. Expected one of {valid_keys}, but got {invalid_keys}."
        ),
    }

    user = PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    movie = PrimaryKeyRelatedField(queryset=Movie.objects.all(), required=False)
    score = ChoiceField(Rating._meta.get_field("score").choices, required=False)

    class Meta:
        model = Rating
        fields = [f.name for f in Rating._meta.fields]
        # TODO: advanced search w/ read_only_fields
        read_only_fields = ["created_at", "updated_at"]

        indexable_fields = ("user", "movie", "score")

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


class ReviewCreateSerializer(ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class ReviewUpdateSerializer(ModelSerializer):
    class Meta(ReviewCreateSerializer.Meta):
        read_only_fields = [
            "user",
            "movie",
        ] + ReviewCreateSerializer.Meta.read_only_fields


class ReviewListSerializer(UseIndexedListSerializerMixin, ModelSerializer):
    default_error_messages = {
        **ModelSerializer.default_error_messages,
        "undefined": _(
            "Query key not allowed. Expected one of {valid_keys}, but got {invalid_keys}."
        ),
    }

    user = PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    movie = PrimaryKeyRelatedField(queryset=Movie.objects.all(), required=False)

    class Meta:
        model = Review
        fields = [f.name for f in Review._meta.fields]
        # TODO: advanced search w/ read_only_fields
        read_only_fields = ["created_at", "updated_at", "comment"]

        indexable_fields = ("user", "movie", "has_spoiler")

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


class WishlistCreateSerializer(ModelSerializer):
    class Meta:
        model = Wishlist
        fields = "__all__"
        read_only_fields = ["timestamp"]


class BlocklistCreateSerializer(ModelSerializer):
    class Meta:
        model = Blocklist
        fields = "__all__"
        read_only_fields = ["timestamp"]
