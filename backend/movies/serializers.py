from __future__ import annotations

from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework.serializers import (
    CharField,
    IntegerField,
    ModelSerializer,
    PrimaryKeyRelatedField,
)

from .mixins.serializer import GetOrSaveMixin, NestedThroughModelMixin
from .models import Country, Credit, Genre, Movie, People, Poster, Still, Video


class GenreSerializer(GetOrSaveMixin, ModelSerializer):
    name = CharField(max_length=7)

    class Meta:
        model = Genre
        fields = "__all__"


class CountrySerializer(GetOrSaveMixin, ModelSerializer):
    alpha_2 = CharField(max_length=2)

    class Meta:
        model = Country
        fields = "__all__"


class PosterSerializer(ModelSerializer):
    movie = PrimaryKeyRelatedField(queryset=Movie.objects.all(), required=False)

    class Meta:
        model = Poster
        fields = "__all__"


class StillSerializer(ModelSerializer):
    movie = PrimaryKeyRelatedField(queryset=Movie.objects.all(), required=False)

    class Meta:
        model = Still
        fields = "__all__"


class VideoSerializer(ModelSerializer):
    movie = PrimaryKeyRelatedField(queryset=Movie.objects.all(), required=False)

    class Meta:
        model = Video
        fields = "__all__"


class PeopleSerializer(GetOrSaveMixin, ModelSerializer):
    tmdb_id = IntegerField(allow_null=True, required=False)
    kmdb_id = CharField(allow_null=True, max_length=8, required=False)

    class Meta:
        model = People
        fields = "__all__"


class CreditSerializer(WritableNestedModelSerializer):
    movie = PrimaryKeyRelatedField(queryset=Movie.objects.all(), required=False)
    people = PeopleSerializer()

    class Meta:
        model = Credit
        fields = "__all__"


class MovieRegisterSerializer(NestedThroughModelMixin, WritableNestedModelSerializer):
    # m-to-m
    countries = CountrySerializer(many=True, required=False)
    genres = GenreSerializer(many=True, required=False)
    staffs = CreditSerializer(many=True)  # w/ through model
    # 1-to-m
    poster_set = PosterSerializer(many=True, required=False)
    still_set = StillSerializer(many=True, required=False)
    video_set = VideoSerializer(many=True, required=False)

    class Meta:
        model = Movie
        fields = "__all__"
