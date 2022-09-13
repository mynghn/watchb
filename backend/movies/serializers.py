from __future__ import annotations

import datetime

from dateutil.relativedelta import relativedelta
from django.core.validators import (
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
    RegexValidator,
)
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework.serializers import (
    CharField,
    DateField,
    DurationField,
    IntegerField,
    ModelSerializer,
    PrimaryKeyRelatedField,
    URLField,
    ValidationError,
)
from rest_framework.validators import UniqueValidator

from movies.decorators import validate_fields

from .mixins.serializer import GetOrSaveMixin, IDsFromAPIValidateMixin
from .models import Country, Credit, Genre, Movie, People, Poster, Still, Video
from .validators import CountryCodeValidator, OnlyKoreanValidator, validate_kmdb_text


class GenreGetOrRegisterSerializer(GetOrSaveMixin, ModelSerializer):
    custom_validators = {"name": {"ko": OnlyKoreanValidator(allowed=r"[/() ]")}}

    name = CharField(
        max_length=7,
        validators=[custom_validators["name"]["ko"]],
    )

    class Meta:
        model = Genre
        fields = "__all__"


class CountryGetOrRegisterSerializer(GetOrSaveMixin, ModelSerializer):
    custom_validators = {
        "alpha_2": {"country_code": CountryCodeValidator(code_type="alpha_2")},
        "name": {"ko": OnlyKoreanValidator(allowed=r"[ ]")},
    }

    alpha_2 = CharField(
        max_length=2, validators=[custom_validators["alpha_2"]["country_code"]]
    )
    name = CharField(
        max_length=50,
        validators=[custom_validators["name"]["ko"]],
    )

    class Meta:
        model = Country
        fields = "__all__"

    def validate_alpha_2(self, value: str) -> str:
        return value.upper()


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
    custom_validators = {"external_id": {"min_length": MinLengthValidator(11)}}

    movie = PrimaryKeyRelatedField(queryset=Movie.objects.all(), required=False)
    external_id = CharField(
        max_length=11,
        validators=[custom_validators["external_id"]["min_length"]],
    )

    class Meta:
        model = Video
        fields = "__all__"


@validate_fields(fields=["name"], validator=validate_kmdb_text)
class PeopleSerializer(GetOrSaveMixin, ModelSerializer):
    custom_validators = {
        "kmdb_id": {"fmt": RegexValidator(regex=r"^[0-9]{8}$")},
        "name": {"ko": OnlyKoreanValidator(allowed=r"\s[A-Z][.]\s|[- ]")},
        "en_name": {"en": RegexValidator(regex=r"[A-Za-zÀ-ÿ.- ]")},
    }

    tmdb_id = IntegerField(allow_null=True, required=False)
    kmdb_id = CharField(
        allow_null=True,
        allow_blank=True,
        max_length=8,
        required=False,
        validators=[custom_validators["kmdb_id"]["fmt"]],
    )
    name = CharField(
        max_length=50,
        trim_whitespace=True,
        validators=[custom_validators["name"]["ko"]],
    )
    en_name = CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        trim_whitespace=True,
        validators=[custom_validators["en_name"]["en"]],
    )
    avatar_url = URLField(
        allow_blank=True, allow_null=True, max_length=200, required=False
    )

    class Meta:
        model = People
        exclude = ["id"]


class PeopleFromAPISerializer(IDsFromAPIValidateMixin, PeopleSerializer):
    api_id_fields = {"tmdb_id", "kmdb_id"}


@validate_fields(fields=["role_name"], validator=validate_kmdb_text)
class CreditSerializer(WritableNestedModelSerializer):
    custom_validators = {"role_name": {"ko": OnlyKoreanValidator(allowed=r"[/- ]")}}

    movie = PrimaryKeyRelatedField(queryset=Movie.objects.all(), required=False)
    people = PeopleSerializer()
    role_name = CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        trim_whitespace=True,
        validators=[custom_validators["role_name"]["ko"]],
    )

    class Meta:
        model = Credit
        fields = "__all__"


class CreditFromAPISerializer(CreditSerializer):
    people = PeopleFromAPISerializer()


@validate_fields(fields=["title"], validator=validate_kmdb_text)
class MovieRegisterSerializer(WritableNestedModelSerializer):
    custom_validators = {
        "kmdb_id": {
            "fmt": RegexValidator(regex=r"^[A-Z]\/[0-9]{5}$"),
            "unique": UniqueValidator(queryset=Movie.objects.all()),
        },
        "release_date": {
            "min_value": MinValueValidator(datetime.date(1895, 3, 22)),
            "max_value": MaxValueValidator(
                lambda: datetime.date.today() + relativedelta(years=5)
            ),
        },
        "production_year": {
            "min_value": MinValueValidator(1850),
            "max_value": MaxValueValidator(lambda: datetime.date.today().year + 3),
        },
        "running_time": {"min_value": MinValueValidator(datetime.timedelta())},
    }

    kmdb_id = CharField(
        allow_null=True,
        allow_blank=True,
        max_length=8,
        required=False,
        validators=list(custom_validators["kmdb_id"].values()),
    )
    title = CharField(max_length=200, trim_whitespace=True)
    synopsys = CharField(allow_blank=True, required=False, trim_whitespace=True)
    release_date = DateField(
        allow_null=True,
        required=False,
        validators=list(custom_validators["release_date"].values()),
    )
    production_year = IntegerField(
        required=False,
        allow_null=True,
        validators=list(custom_validators["production_year"].values()),
    )
    running_time = DurationField(
        allow_null=True,
        required=False,
        validators=[custom_validators["running_time"]["min_value"]],
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

    def validate_poster_set(self, value: list[dict[str, str]]) -> list[dict[str, str]]:
        main_cnt = 0
        image_url_set = set()
        for poster in value:
            if poster["is_main"]:
                if main_cnt == 0:
                    main_cnt += 1
                else:
                    raise ValidationError(
                        "more than one main poster in a movie", code="unique"
                    )

            if (p_image_url := poster["image_url"]) not in image_url_set:
                image_url_set.add(p_image_url)
            else:
                raise ValidationError(
                    f"redundant poster image_url in a movie: {p_image_url}",
                    code="unique",
                )

        return value

    def validate_still_set(self, value: list[dict[str, str]]) -> list[dict[str, str]]:
        image_url_set = set()
        for still in value:
            if (s_image_url := still["image_url"]) not in image_url_set:
                image_url_set.add(s_image_url)
            else:
                raise ValidationError(
                    f"redundant still image_url in a movie: {s_image_url}",
                    code="unique",
                )

        return value

    def validate_video_set(self, value: list[dict[str, str]]) -> list[dict[str, str]]:
        title_set = set()
        site_and_external_id_set = set()
        for video in value:
            if v_title := video.get("titlie"):
                if v_title not in title_set:
                    title_set.add(v_title)
                else:
                    raise ValidationError(
                        f"redundant video title in a movie: {v_title}", code="unique"
                    )
            if (
                v_identifier := (video["site"], video["external_id"])
            ) not in site_and_external_id_set:
                site_and_external_id_set.add(v_identifier)
            else:
                raise ValidationError(
                    f"redundant video in a movie: {v_identifier}",
                    code="unique",
                )

        return value


class MovieFromAPISerializer(IDsFromAPIValidateMixin, MovieRegisterSerializer):
    api_id_fields = {"tmdb_id", "kmdb_id"}
