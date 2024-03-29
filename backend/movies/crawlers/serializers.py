from __future__ import annotations

import datetime
import re
from collections import defaultdict
from typing import Optional

from dateutil.relativedelta import relativedelta
from decorators import lazy_load_property, validate_fields
from django.core.validators import (
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
    RegexValidator,
)
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

from serializers import (
    CreateOrMergeWithDataMixin,
    NestedCreateMixin,
    RequiredTogetherMixin,
    SkipChildsListSerializer,
    SkipFieldsMixin,
)

from ..models import Country, Credit, Genre, Movie, Person, Poster, Still, Video
from .utils import ISO_3166_1
from .validators import (
    PERSON_EN_NAME_REGEX,
    CountryCodeValidator,
    OnlyKoreanValidator,
    validate_kmdb_text,
)


class GenreCreateOrMergeSerializer(CreateOrMergeWithDataMixin, ModelSerializer):
    class Meta:
        model = Genre
        fields = "__all__"
        list_serializer_class = SkipChildsListSerializer
        custom_validators = {"name": {"ko": OnlyKoreanValidator(allowed=r"[/() ]|SF")}}

    name = CharField(max_length=10, validators=[Meta.custom_validators["name"]["ko"]])


class CountryCreateOrMergeSerializer(CreateOrMergeWithDataMixin, ModelSerializer):
    alpha_2 = CharField(max_length=2, required=False)
    name = CharField(max_length=17, required=False)

    class Meta:
        model = Country
        fields = "__all__"
        list_serializer_class = SkipChildsListSerializer

    _name_map = {"대한민국": "한국"}

    @lazy_load_property
    def reverse_name_map(self) -> dict[str, str]:
        return {v: k for k, v in self._name_map.items()}

    alpha_2_validator = CountryCodeValidator("alpha_2")

    def validate_alpha_2(self, value: Optional[str]) -> Optional[str]:
        if value:
            if value.upper() == "SU":  # 소련 -> 러시아로
                return "RU"
            else:
                self.alpha_2_validator(value)
        return value

    def validate_name(self, value: Optional[str]) -> Optional[str]:
        if not value:
            return value
        elif value in self._name_map.values() or ISO_3166_1.get_country(name=value):
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
                iso_name := ISO_3166_1.get_country(alpha_2=alpha_2)[
                    ISO_3166_1.name_key
                ],
                iso_name,
            )
        elif not alpha_2:
            attrs["alpha2"] = ISO_3166_1.get_country(
                name=self.reverse_name_map.get(name, name)
            )[ISO_3166_1.alpha_2_key]
        return super().validate(attrs)


class PosterSerializer(ModelSerializer):
    movie = PrimaryKeyRelatedField(queryset=Movie.objects.all(), required=False)

    class Meta:
        model = Poster
        fields = "__all__"
        list_serializer_class = SkipChildsListSerializer


class StillSerializer(ModelSerializer):
    movie = PrimaryKeyRelatedField(queryset=Movie.objects.all(), required=False)

    class Meta:
        model = Still
        fields = "__all__"
        list_serializer_class = SkipChildsListSerializer


class VideoSerializer(ModelSerializer):
    class Meta:
        model = Video
        fields = "__all__"
        list_serializer_class = SkipChildsListSerializer
        custom_validators = {"external_id": {"min_length": MinLengthValidator(11)}}

    movie = PrimaryKeyRelatedField(queryset=Movie.objects.all(), required=False)
    external_id = CharField(
        max_length=11,
        validators=[Meta.custom_validators["external_id"]["min_length"]],
    )


class PersonCreateOrMergeSerializer(
    SkipFieldsMixin, CreateOrMergeWithDataMixin, ModelSerializer
):
    class Meta:
        model = Person
        fields = "__all__"
        can_skip_fields = {"en_name"}
        custom_validators = {
            "kmdb_id": {"fmt": RegexValidator(regex=r"^[0-9]{8}$")},
            "en_name": {
                "en": RegexValidator(
                    regex=PERSON_EN_NAME_REGEX,
                    message="Invalid Person en_name '%(value)s' encountered.",
                )
            },
        }

    id = IntegerField(label="ID", required=False)
    tmdb_id = IntegerField(allow_null=True, required=False)
    kmdb_id = CharField(
        max_length=8,
        required=False,
        allow_null=True,
        trim_whitespace=True,
        validators=[Meta.custom_validators["kmdb_id"]["fmt"]],
    )
    name = CharField(
        max_length=30, required=False, allow_blank=True, trim_whitespace=True
    )
    en_name = CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        trim_whitespace=True,
        validators=[Meta.custom_validators["en_name"]["en"]],
    )
    avatar_url = URLField(allow_null=True, max_length=200, required=False)

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
class PersonFromAPISerializer(RequiredTogetherMixin, PersonCreateOrMergeSerializer):
    class Meta(PersonCreateOrMergeSerializer.Meta):
        fields = None
        exclude = ["id"]
        required_together_fields = ["tmdb_id", "kmdb_id"]

    id = None
    en_name = CharField(
        max_length=50, required=False, allow_blank=True, trim_whitespace=True
    )

    def validate_en_name(self, value: str) -> str:
        if value:
            self.Meta.custom_validators["en_name"]["en"](value)
        return value


class CreditSerializer(SkipFieldsMixin, NestedCreateMixin, ModelSerializer):

    movie = PrimaryKeyRelatedField(queryset=Movie.objects.all(), required=False)
    person = PersonCreateOrMergeSerializer()
    role_name = CharField(
        max_length=200, required=False, allow_blank=True, trim_whitespace=True
    )

    class Meta:
        model = Credit
        fields = "__all__"
        list_serializer_class = SkipChildsListSerializer
        can_skip_fields = {"role_name"}


@validate_fields(fields=["role_name"], validator=validate_kmdb_text)
class CreditFromAPISerializer(CreditSerializer):
    person = PersonFromAPISerializer()
    role_name = CharField(
        max_length=200, required=False, allow_blank=True, trim_whitespace=True
    )


special_characters = r",.?!;:'\"₩~@#$%^&_\-+*/=|(){}\[\]<>/\\"


class MovieRegisterSerializer(SkipFieldsMixin, NestedCreateMixin, ModelSerializer):
    class Meta:
        model = Movie
        fields = "__all__"
        can_skip_fields = {"release_date"}
        remove_redundancy = True
        custom_validators = {
            "title": {
                "ko_and_more": RegexValidator(
                    regex=r"[가-힣]+|"
                    rf"^[A-Z0-9{special_characters} ]+$|"
                    rf"^[a-zA-Z0-9{special_characters}]+$",
                    message="Invalid Movie title '%(value)s' encountered.",
                ),
            },
            "kmdb_id": {"fmt": RegexValidator(regex=r"^[A-Z]\/[0-9]{5}$")},
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
        max_length=7,
        required=False,
        allow_null=True,
        trim_whitespace=True,
        validators=[
            Meta.custom_validators["kmdb_id"]["fmt"],
            UniqueValidator(queryset=Movie.objects.all()),
        ],
    )
    title = CharField(
        max_length=50,
        trim_whitespace=True,
        validators=[Meta.custom_validators["title"]["ko_and_more"]],
    )
    synopsys = CharField(allow_blank=True, required=False, trim_whitespace=True)
    release_date = DateField(
        allow_null=True,
        required=False,
        validators=list(Meta.custom_validators["release_date"].values()),
    )
    production_year = IntegerField(
        required=False,
        allow_null=True,
        validators=list(Meta.custom_validators["production_year"].values()),
    )
    running_time = DurationField(
        allow_null=True,
        required=False,
        validators=[Meta.custom_validators["running_time"]["min_value"]],
    )
    # m-to-m
    countries = CountryCreateOrMergeSerializer(many=True, required=False)
    genres = GenreCreateOrMergeSerializer(many=True, required=False)
    credits = CreditSerializer(many=True, allow_empty=False)  # w/ through model
    # 1-to-m
    poster_set = PosterSerializer(many=True, required=False)
    still_set = StillSerializer(many=True, required=False)
    video_set = VideoSerializer(many=True, required=False)

    def validate_poster_set(self, value: list[dict[str, str]]) -> list[dict[str, str]]:
        main_cnt = 0
        image_url_set = set()
        validated = []
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
                validated.append(poster)
            elif not self.Meta.remove_redundancy:
                raise ValidationError(
                    f"redundant poster image_url in a movie: {p_image_url}",
                    code="unique",
                )

        return validated

    def validate_still_set(self, value: list[dict[str, str]]) -> list[dict[str, str]]:
        image_url_set = set()
        validated = []
        for still in value:
            if (s_image_url := still["image_url"]) not in image_url_set:
                image_url_set.add(s_image_url)
                validated.append(still)
            elif not self.Meta.remove_redundancy:
                raise ValidationError(
                    f"redundant still image_url in a movie: {s_image_url}",
                    code="unique",
                )

        return validated

    def validate_video_set(self, value: list[dict[str, str]]) -> list[dict[str, str]]:
        title_set = set()
        site_and_external_id_set = set()
        validated = []
        for video in value:
            if v_title := video.get("title", ""):
                if v_title not in title_set:
                    title_set.add(v_title)
                elif not self.Meta.remove_redundancy:
                    raise ValidationError(
                        f"redundant video title in a movie: {v_title}", code="unique"
                    )
                else:
                    continue
            if (
                v_identifier := (video["site"], video["external_id"])
            ) not in site_and_external_id_set:
                site_and_external_id_set.add(v_identifier)
            elif not self.Meta.remove_redundancy:
                raise ValidationError(
                    f"redundant video in a movie: {v_identifier}", code="unique"
                )
            else:
                continue

            validated.append(video)

        return validated

    def validate_credits(
        self, value: list[dict[str, str | dict[str, str | int]]]
    ) -> list[dict[str, str | dict[str, str | int]]]:
        if not value:
            raise ValidationError(
                "Movie should have at least one credit.", code="invalid"
            )
        elif not any(credit["job"] == "director" for credit in value):
            raise ValidationError(
                "Movie should have at least one director.", code="invalid"
            )
        else:
            return value


@validate_fields(fields=["title", "synopsys"], validator=validate_kmdb_text)
class MovieFromAPISerializer(RequiredTogetherMixin, MovieRegisterSerializer):
    class Meta(MovieRegisterSerializer.Meta):
        required_together_fields = ["tmdb_id", "kmdb_id"]
        title_max_length = 50

    title = CharField(trim_whitespace=True)
    release_date = DateField(
        input_formats=["%Y-%m-%dT%H:%M:%S.%fZ", "%Y%m%d", ISO_8601],
        allow_null=True,
        required=False,
        validators=list(
            MovieRegisterSerializer.Meta.custom_validators["release_date"].values()
        ),
    )
    production_year = CharField(max_length=8, allow_null=True, required=False)
    credits = CreditFromAPISerializer(many=True)

    def validate_title(self, value: str) -> str:
        # 1. max_length
        if len(value) > self.Meta.title_max_length:
            raise ValidationError(
                f"Movie title '{value}' has more than {self.Meta.title_max_length} characters.",
                code="max_length",
            )
        else:  # 2. regex
            self.Meta.custom_validators["title"]["ko_and_more"](value)
        return value

    def validate_credits(
        self, value: list[dict[str, str | dict[str, str | int]]]
    ) -> list[dict[str, str | dict[str, str | int]]]:
        value = super(MovieFromAPISerializer, self).validate_credits(value)
        credits_by_job = defaultdict(list)
        for c in value:
            credits_by_job[c["job"]].append(c)
        validated = []
        for job, credits in credits_by_job.items():
            if job == "actor":
                roles_by_actor = defaultdict(set)
                no_roles = []
                for c in credits:
                    person_api_id = c["person"].get("tmdb_id") or c["person"].get(
                        "kmdb_id"
                    )
                    if not c.get("role_name"):
                        no_roles.append(c)
                    elif c["role_name"] not in roles_by_actor[person_api_id]:
                        validated.append(c)
                        roles_by_actor[person_api_id].add(c["role_name"])
                    elif not self.Meta.remove_redundancy:
                        raise ValidationError(
                            f"same credit among cast: {c}", code="unique"
                        )
                for c in no_roles:
                    if not roles_by_actor[
                        c["person"].get("tmdb_id") or c["person"].get("kmdb_id")
                    ]:
                        validated.append(c)
                    elif not self.Meta.remove_redundancy:
                        raise ValidationError(
                            f"same credit among cast: {c}", code="unique"
                        )
            else:
                staff_id_set = set()
                for c in credits:
                    person_api_id = c["person"].get("tmdb_id") or c["person"].get(
                        "kmdb_id"
                    )
                    if person_api_id not in staff_id_set:
                        validated.append(c)
                        staff_id_set.add(person_api_id)
                    elif not self.Meta.remove_redundancy:
                        raise ValidationError(
                            f"same person among {job}s: {c}", code="unique"
                        )

        return validated

    def validate_production_year(self, value: str) -> Optional[int]:
        if value:
            if len(value) <= 4:
                return int(value)
            else:
                try:
                    datetime.datetime.strptime(value, "%Y%m%d")
                except ValueError as e:
                    if not (
                        re.match(r"time data '[^']+' does not match format", e.args[0])
                        and len(value) == 8
                        and value[4:6] == value[6:8] == "00"
                    ):
                        raise ValidationError(f"Invalid value: {value}", code="invalid")
                finally:
                    return int(value[:4])
