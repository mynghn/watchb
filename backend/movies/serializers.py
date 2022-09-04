from __future__ import annotations

import datetime

from dateutil.relativedelta import relativedelta
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework.serializers import (
    CharField,
    DateField,
    DurationField,
    IntegerField,
    ModelSerializer,
    PrimaryKeyRelatedField,
    URLField,
)
from rest_framework.validators import UniqueValidator

from movies.decorators import validate_fields

from .mixins.serializer import GetOrSaveMixin, IDsFromAPIValidateMixin
from .models import Country, Credit, Genre, Movie, People, Poster, Still, Video
from .validators import CountryCodeValidator, OnlyKoreanValidator, validate_kmdb_text


class GenreGetOrRegisterSerializer(GetOrSaveMixin, ModelSerializer):
    name = CharField(
        max_length=7,
        validators=[OnlyKoreanValidator(allowed=r"[/() ]")],
    )

    class Meta:
        model = Genre
        fields = "__all__"


class CountryGetOrRegisterSerializer(GetOrSaveMixin, ModelSerializer):
    alpha_2 = CharField(
        max_length=2, validators=[CountryCodeValidator(code_type="alpha_2")]
    )
    name = CharField(
        max_length=50,
        validators=[OnlyKoreanValidator(allowed=r"[ ]")],
    )

    class Meta:
        model = Country
        fields = "__all__"

    def validate_alpha_2(self, value: str) -> str:
        return value.capitalize()


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
    video_url = URLField(
        max_length=200,
        validators=[
            UniqueValidator(queryset=Video.objects.all()),
            RegexValidator(regex=r"^https:\/\/www\.youtube\.com\/watch\?v=\w+$"),
        ],
    )
    thumbnail_url = URLField(
        max_length=200,
        validators=[
            UniqueValidator(queryset=Video.objects.all()),
            RegexValidator(regex=r"^https:\/\/img\.youtube\.com\/vi\/\w+?\/\d\.jpg$"),
        ],
    )

    class Meta:
        model = Video
        fields = "__all__"


@validate_fields(fields=["name"], validator=validate_kmdb_text)
class PeopleGetOrRegisterSerializer(GetOrSaveMixin, ModelSerializer):
    tmdb_id = IntegerField(allow_null=True, required=False)
    kmdb_id = CharField(
        allow_null=True,
        max_length=8,
        required=False,
        validators=[RegexValidator(regex=r"^[0-9]{8}$")],
    )
    name = CharField(
        max_length=50,
        trim_whitespace=True,
        validators=[OnlyKoreanValidator(allowed=r" (!HS|!HE) |[ -]")],
    )

    fields_to_clean = ["name"]

    class Meta:
        model = People
        fields = "__all__"


class PeopleFromAPISerializer(IDsFromAPIValidateMixin, PeopleGetOrRegisterSerializer):
    api_id_fields = {"tmdb_id", "kmdb_id"}


@validate_fields(fields=["role_name"], validator=validate_kmdb_text)
class CreditSerializer(WritableNestedModelSerializer):
    movie = PrimaryKeyRelatedField(queryset=Movie.objects.all(), required=False)
    people = PeopleGetOrRegisterSerializer()
    role_name = CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        trim_whitespace=True,
        validators=[OnlyKoreanValidator(allowed=r" (!HS|!HE) |[ /]")],
    )

    class Meta:
        model = Credit
        fields = "__all__"


class CreditFromAPISerializer(CreditSerializer):
    people = PeopleFromAPISerializer()


@validate_fields(fields=["title"], validator=validate_kmdb_text)
class MovieRegisterSerializer(WritableNestedModelSerializer):
    kmdb_id = CharField(
        allow_null=True,
        max_length=8,
        required=False,
        validators=[RegexValidator(regex=r"^[A-Z]\/[0-9]{5}$")],
    )
    title = CharField(max_length=200, trim_whitespace=True)
    synopsys = CharField(allow_blank=True, required=False, trim_whitespace=True)
    release_date = DateField(
        allow_null=True,
        required=False,
        validators=[
            MinValueValidator(datetime.date(1895, 3, 22)),
            MaxValueValidator(lambda: datetime.date.today() + relativedelta(years=5)),
        ],
    )
    running_time = DurationField(
        allow_null=True,
        required=False,
        validators=[MinValueValidator(datetime.timedelta())],
    )
    # m-to-m
    countries = CountryGetOrRegisterSerializer(many=True, required=False)
    genres = GenreGetOrRegisterSerializer(many=True, required=False)
    credits = CreditFromAPISerializer(many=True)  # w/ through model
    # 1-to-m
    poster_set = PosterSerializer(many=True, required=False)
    still_set = StillSerializer(many=True, required=False)
    video_set = VideoSerializer(many=True, required=False)

    class Meta:
        model = Movie
        fields = "__all__"


class MovieFromAPISerializer(IDsFromAPIValidateMixin, MovieRegisterSerializer):
    api_id_fields = {"tmdb_id", "kmdb_id"}
