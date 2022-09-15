from __future__ import annotations

import datetime
from collections import defaultdict
from typing import Optional

from dateutil.relativedelta import relativedelta
from django.core.validators import (
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
    RegexValidator,
)
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import ISO_8601
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
from rest_framework.settings import api_settings
from rest_framework.validators import UniqueValidator

from movies.crawlers.utils import ISO_3166_1
from movies.decorators import lazy_load_property, validate_fields

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
        max_length=2,
        required=False,
        validators=[custom_validators["alpha_2"]["country_code"]],
    )
    name = CharField(
        max_length=50,
        required=False,
        validators=[custom_validators["name"]["ko"]],
    )

    class Meta:
        model = Country
        fields = "__all__"

    _name_map = {"대한민국": "한국"}

    @lazy_load_property
    def reverse_name_map(self) -> dict[str, str]:
        return {v: k for k, v in self._name_map.items()}

    def validate_alpha_2(self, value: str) -> str:
        if not value:
            return value
        elif ISO_3166_1.get_country(value):
            return value.upper()
        else:
            raise ValidationError(
                f"'{value}' is not a valid ISO 3166-1 alpha-2 country code.",
                code="invalid",
            )

    def validate_name(self, value: str) -> str:
        if not value:
            return value
        elif value in self._name_map.values() or ISO_3166_1.get_country(value):
            return self._name_map.get(value, value)
        else:
            raise ValidationError(
                f"'{value}' is not a valid ISO 3166-1 country name.",
                code="invalid",
            )

    def validate(self, attrs: dict[str, Optional[str]]) -> dict[str, str]:
        alpha_2 = attrs.get("alpha_2")
        name = attrs.get("name")
        if not alpha_2 and not name:
            raise ValidationError(
                {
                    api_settings.NON_FIELD_ERRORS_KEY: [
                        "At least one of 'alpha_2' or 'name' field is required."
                    ]
                },
                code="required",
            )
        elif not name:
            attrs["name"] = self._name_map.get(
                iso_name := ISO_3166_1.get_country(alpha_2)[ISO_3166_1.name_key],
                iso_name,
            )
        elif not alpha_2:
            attrs["alpha2"] = ISO_3166_1.get_country(
                self.reverse_name_map.get(name, name)
            )[ISO_3166_1.alpha2_key]
        return super().validate(attrs)


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


class PeopleGetOrRegisterSerializer(GetOrSaveMixin, ModelSerializer):
    custom_validators = {
        "kmdb_id": {"fmt": RegexValidator(regex=r"^[0-9]{8}$")},
        "en_name": {"en": RegexValidator(regex=r"[A-Za-zÀ-ÿ.- ]")},
    }

    id = IntegerField(label="ID", required=False)
    tmdb_id = IntegerField(allow_null=True, required=False)
    kmdb_id = CharField(
        max_length=8,
        required=False,
        allow_null=True,
        allow_blank=True,
        trim_whitespace=True,
        validators=[custom_validators["kmdb_id"]["fmt"]],
    )
    name = CharField(max_length=50, allow_blank=True, trim_whitespace=True)
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
        fields = "__all__"

    def validate(self, attrs: dict[str, str | int]) -> dict[str, str | int]:
        if not attrs.get("name") and not attrs.get("en_name"):
            raise ValidationError(
                {
                    api_settings.NON_FIELD_ERRORS_KEY: [
                        "At least one of 'name' or 'en_name' field is required."
                    ]
                },
                code="required",
            )
        return super().validate(attrs)


@validate_fields(fields=["name", "en_name"], validator=validate_kmdb_text)
class PeopleFromAPISerializer(IDsFromAPIValidateMixin, PeopleGetOrRegisterSerializer):
    api_id_fields = {"tmdb_id", "kmdb_id"}

    custom_validators = {
        "en_name": {"en": RegexValidator(regex=r"[A-Za-zÀ-ÿ.-]|\s|!HS|!HE")},
    }

    id = None
    name = CharField(max_length=50, required=False, trim_whitespace=True)
    en_name = CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        trim_whitespace=True,
        validators=[custom_validators["en_name"]["en"]],
    )

    class Meta(PeopleGetOrRegisterSerializer.Meta):
        fields = None
        exclude = ["id"]


class CreditSerializer(WritableNestedModelSerializer):

    movie = PrimaryKeyRelatedField(queryset=Movie.objects.all(), required=False)
    people = PeopleGetOrRegisterSerializer()
    role_name = CharField(
        max_length=50, required=False, allow_blank=True, trim_whitespace=True
    )

    class Meta:
        model = Credit
        fields = "__all__"


@validate_fields(fields=["role_name"], validator=validate_kmdb_text)
class CreditFromAPISerializer(CreditSerializer):
    people = PeopleFromAPISerializer()
    role_name = CharField(
        max_length=50, required=False, allow_blank=True, trim_whitespace=True
    )


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
        max_length=8,
        required=False,
        allow_null=True,
        allow_blank=True,
        trim_whitespace=True,
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
    credits = CreditSerializer(many=True)  # w/ through model
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


@validate_fields(fields=["title", "synopsys"], validator=validate_kmdb_text)
class MovieFromAPISerializer(IDsFromAPIValidateMixin, MovieRegisterSerializer):
    api_id_fields = {"tmdb_id", "kmdb_id"}

    release_date = DateField(
        input_formats=["%Y-%m-%dT%H:%M:%S.%fZ", "%Y%m%d", ISO_8601],
        allow_null=True,
        required=False,
        validators=list(
            MovieRegisterSerializer.custom_validators["release_date"].values()
        ),
    )
    production_year = CharField(max_length=8, allow_null=True, required=False)
    credits = CreditFromAPISerializer(many=True)

    def validate_credits(
        self, value: list[dict[str, str | dict[str, str | int]]]
    ) -> list[dict[str, str | dict[str, str | int]]]:
        credits_by_job = defaultdict(list)
        for c in value:
            credits_by_job[c["job"]].append(c)

        for job, credits in credits_by_job.items():
            if job == "actor":
                roles_by_actor = defaultdict(list)
                for c in credits:
                    roles_by_actor[
                        c["people"].get("tmdb_id") or c["people"].get("kmdb_id")
                    ].append(c["role_name"])
                if any(
                    len(roles) > 1
                    and (any(not r for r in roles) or len(set(roles)) != len(roles))
                    for roles in roles_by_actor.values()
                ):
                    raise ValidationError(
                        f"same credit among cast: {credits}", code="unique"
                    )
            elif len(
                set(
                    c["people"].get("tmdb_id") or c["people"].get("kmdb_id")
                    for c in credits
                )
            ) != len(credits):
                raise ValidationError(
                    f"same person among {job}s: {credits}", code="unique"
                )
        return value

    def validate_production_year(self, value: str) -> int:
        if len(value) <= 4:
            return int(value)
        else:
            try:
                datetime.datetime.strptime(value, "%Y%m%d")
            except ValueError:
                raise ValidationError(f"Invalid value: {value}", code="invalid")
            else:
                return int(value[:4])
