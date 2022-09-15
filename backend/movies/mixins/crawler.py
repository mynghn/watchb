from __future__ import annotations

import datetime
import re
from collections import defaultdict
from typing import Any, DefaultDict, Iterable, Literal, Optional, Type

from ..agents import KMDbAPIAgent, TMDBAPIAgent
from ..crawlers.interface import APICrawler, ListAndDetailCrawler
from ..custom_types import (
    EnglishName,
    MovieFromAPI,
    MovieFromKMDb,
    MovieFromTMDB,
    SerializedCreditFromAPI,
    SerializedPeopleFromAPI,
    SimpleMovieFromTMDB,
)
from ..models import Credit, Movie, People
from ..serializers import MovieFromAPISerializer, PeopleFromAPISerializer
from ..validators import validate_kmdb_text


class PopularListMixin(ListAndDetailCrawler):
    tmdb_agent: TMDBAPIAgent

    def list(self, max_count: Optional[int] = None) -> list[SimpleMovieFromTMDB]:
        return self.tmdb_agent.popular_movies(max_count=max_count)


class TrendingListMixin(ListAndDetailCrawler):
    tmdb_agent: TMDBAPIAgent

    def list(
        self,
        time_window: Literal["day", "week"] = "week",
        max_count: Optional[int] = None,
    ) -> list[SimpleMovieFromTMDB]:
        return self.tmdb_agent.trending_movies(
            time_window=time_window, max_count=max_count
        )


class TopRatedListMixin(ListAndDetailCrawler):
    tmdb_agent: TMDBAPIAgent

    def list(self, max_count: Optional[int] = None) -> list[SimpleMovieFromTMDB]:
        return self.tmdb_agent.top_rated_movies(max_count=max_count)


class NowPlayingListMixin(ListAndDetailCrawler):
    tmdb_agent: TMDBAPIAgent

    def list(self, max_count: Optional[int] = None) -> list[SimpleMovieFromTMDB]:
        return self.tmdb_agent.now_playing_movies(max_count=max_count)


class SearchListMixin(ListAndDetailCrawler):
    tmdb_agent: TMDBAPIAgent

    def list(
        self, query: str, year: Optional[int] = None, max_count: Optional[int] = None
    ) -> list[SimpleMovieFromTMDB]:
        return self.tmdb_agent.search_movies(
            query=query, year=year, max_count=max_count
        )


class FieldLevelSerializeMixin(APICrawler):
    fields_to_serialize: Iterable[str]

    def serialize(
        self,
        movie_fetched: MovieFromAPI,
        fields: list = [],
        filtered: Optional[bool] = None,
        cls: Optional[Type[FieldLevelSerializeMixin]] = None,
    ) -> dict[str, Any]:
        return {
            fname: serialized
            for fname in fields or self.fields_to_serialize
            if (
                (
                    serializer := getattr(
                        cls or self.__class__, f"serialize_{fname}", False
                    )
                )
                and (serialized := serializer(self, movie_fetched, filtered=filtered))
            )
        }


# TODO: SerializeMixin들 DRF Serializer 사용해서 재정의


class TMDBSerializeMixin(FieldLevelSerializeMixin):
    fields_to_serialize = [
        "tmdb_id",
        "title",
        "release_date",
        "genres",
        "countries",
        "running_time",
        "synopsys",
        "credits",
        "poster_set",
        "still_set",
        "video_set",
    ]

    filtered: bool = True
    tmdb_agent: TMDBAPIAgent

    def serialize_tmdb_id(self, movie_fetched: MovieFromTMDB, **kwargs) -> int:
        return movie_fetched.id

    def serialize_title(self, movie_fetched: MovieFromTMDB, **kwargs) -> str:
        return movie_fetched.title

    def serialize_release_date(
        self, movie_fetched: MovieFromTMDB, **kwargs
    ) -> Optional[str]:
        theatrical = None
        digital = None
        for release_date in movie_fetched.kr_release_dates:
            if release_date.type == 2:
                return release_date.release_date
            elif release_date.type == 3:
                theatrical = release_date.release_date
            elif release_date.type == 4:
                digital = release_date.release_date
        return theatrical or digital

    genre_filter = {
        "모험": "어드벤처",
        "애니메이션": False,
        "다큐멘터리": False,
        "역사": False,
        "TV 영화": False,
    }

    def serialize_genres(
        self, movie_fetched: MovieFromTMDB, filtered: Optional[bool] = None
    ) -> list[dict[str, str]]:
        _filtered = self.filtered if filtered is None else filtered
        if _filtered:
            return [
                {"name": g_filtered}
                for g in movie_fetched.genres
                if (g_filtered := TMDBSerializeMixin.genre_filter.get(g.name, g.name))
            ]
        else:
            return [{"name": g.name} for g in movie_fetched.genres]

    def serialize_countries(
        self, movie_fetched: MovieFromTMDB, **kwargs
    ) -> list[dict[str, str]]:
        return [{"alpha_2": c.iso_3166_1} for c in movie_fetched.production_countries]

    def serialize_running_time(
        self, movie_fetched: MovieFromTMDB, **kwargs
    ) -> Optional[str]:
        if movie_fetched.runtime:
            return f"{movie_fetched.runtime}:0"

    def serialize_synopsys(
        self, movie_fetched: MovieFromTMDB, **kwargs
    ) -> Optional[str]:
        return movie_fetched.overview

    def serialize_credits(
        self, movie_fetched: MovieFromTMDB, filtered: Optional[bool] = None
    ) -> list[SerializedCreditFromAPI]:
        _filtered = self.filtered if filtered is None else filtered
        return [
            dict(
                job=staff.job.lower(),
                people=TMDBSerializeMixin.get_or_build_person(self, staff.id),
            )
            for staff in movie_fetched.credits.crew
            if not _filtered or (staff.job.lower() in ("director", "writer"))
        ] + [
            dict(
                job="actor",
                role_name=actor.character,
                people=TMDBSerializeMixin.get_or_build_person(self, actor.id),
            )
            for actor in movie_fetched.credits.cast
        ]

    def serialize_poster_set(
        self, movie_fetched: MovieFromTMDB, filtered: Optional[bool] = None
    ) -> list[dict[str, bool | str]]:
        if not movie_fetched.images.posters:
            return []

        _filtered = self.filtered if filtered is None else filtered
        return [
            {
                "is_main": True,
                "image_url": self.tmdb_agent.image_base_url
                + movie_fetched.images.posters[0].file_path,
            }
        ] + [
            {
                "is_main": False,
                "image_url": self.tmdb_agent.image_base_url + p.file_path,
            }
            for p in movie_fetched.images.posters[1:]
            if not _filtered or not p.iso_639_1 or p.iso_639_1 == "ko"
        ]

    def serialize_still_set(
        self, movie_fetched: MovieFromTMDB, filtered: Optional[bool] = None
    ) -> list[dict[str, str]]:
        _filtered = self.filtered if filtered is None else filtered
        return [
            {"image_url": self.tmdb_agent.image_base_url + s.file_path}
            for s in movie_fetched.images.backdrops
            if not _filtered or not s.iso_639_1 or s.iso_639_1 == "ko"
        ]

    def serialize_video_set(
        self, movie_fetched: MovieFromTMDB, filtered: Optional[bool] = None
    ) -> list[dict]:
        _filtered = self.filtered if filtered is None else filtered
        return [
            {"title": v.name, "site": v.site.lower(), "external_id": v.key}
            for v in movie_fetched.videos.results
            if not _filtered
            or (v.site == "YouTube" and (not v.iso_639_1 or v.iso_639_1 == "ko"))
        ]

    def get_or_build_person(self, tmdb_id: int) -> SerializedPeopleFromAPI:
        if person_in_db := People.objects.filter(tmdb_id=tmdb_id):
            person_json = dict(PeopleFromAPISerializer(person_in_db.get()).data)
        else:
            tmdb_person = self.tmdb_agent.person_detail(tmdb_id)
            # name
            person_json = {"en_name": tmdb_person.name}
            for aka in tmdb_person.also_known_as:
                if re.search(r"[가-힣]", aka):
                    person_json["name"] = aka
                    break
            # id
            person_json["tmdb_id"] = tmdb_id
            # bio
            if bio := tmdb_person.biography:
                person_json["biography"] = bio
            # avatar
            if p := tmdb_person.profile_path:
                person_json["avatar_url"] = self.tmdb_agent.image_base_url + p

        return person_json


class KMDbSerializeMixin(FieldLevelSerializeMixin):
    fields_to_serialize = [
        "kmdb_id",
        "title",
        "release_date",
        "production_year",
        "genres",
        "countries",
        "running_time",
        "synopsys",
        "film_rating",
        "credits",
        "poster_set",
        "still_set",
    ]

    filtered: bool = True

    def serialize_kmdb_id(self, movie_fetched: MovieFromKMDb, **kwargs) -> str:
        return "/".join([movie_fetched.movieId, movie_fetched.movieSeq])

    def serialize_title(self, movie_fetched: MovieFromKMDb, **kwargs) -> str:
        return movie_fetched.title

    def serialize_release_date(
        self, movie_fetched: MovieFromKMDb, **kwargs
    ) -> Optional[str]:
        if movie_fetched.repRlsDate:
            return movie_fetched.repRlsDate

    def serialize_production_year(
        self, movie_fetched: MovieFromKMDb, **kwargs
    ) -> Optional[str]:
        if movie_fetched.prodYear:
            return movie_fetched.repRlsDate

    genre_filter = {"코메디": "코미디", "뮤직": "음악", "멜로/로맨스": "로맨스"}

    def serialize_genres(
        self, movie_fetched: MovieFromKMDb, **kwargs
    ) -> Optional[list[dict[str, str]]]:
        if movie_fetched.genre:
            return [
                {"name": KMDbSerializeMixin.genre_filter.get(gname := g.strip(), gname)}
                for g in movie_fetched.genre.split(",")
            ]

    def serialize_countries(
        self, movie_fetched: MovieFromKMDb, **kwargs
    ) -> Optional[list[dict[str, str]]]:
        if movie_fetched.nation:
            return [{"name": c.strip()} for c in movie_fetched.nation.split(",")]

    def serialize_running_time(
        self, movie_fetched: MovieFromKMDb, **kwargs
    ) -> Optional[str]:
        if movie_fetched.runtime:
            return f"{movie_fetched.runtime}:0"

    def serialize_synopsys(
        self, movie_fetched: MovieFromKMDb, filtered: Optional[bool] = None
    ) -> Optional[str]:
        _filtered = self.filtered if filtered is None else filtered
        if _filtered and (
            kor_plots := [
                plot.plotText
                for plot in movie_fetched.plots.plot
                if plot.plotLang == "한국어"
            ]
        ):
            return max(kor_plots, key=len)
        elif plots := movie_fetched.plots.plot:
            return plots[0].plotText

    rating_choice_map = {
        v: choice
        for choice, verbose in Movie.film_rating.field.choices
        for v in {
            "전체관람가": ["연소자관람가", "국민학생이상관람가", "모두관람가", "미성년자관람가", "전체관람가"],
            "12세이상관람가": ["12세관람가", "12세미만불가", "중학생가", "중학생이상"],
            "15세이상관람가": ["15세관람가", "고등학생가", "고등학생이상관람가", "고등학생이상"],
            "청소년관람불가": ["연소자불가", "연소자관람불가", "18세미만불가", "미성년자관람불가", "18세관람가(청소년관람불가)"],
        }.get(verbose, [verbose])
    }

    def serialize_film_rating(
        self, movie_fetched: MovieFromKMDb, **kwargs
    ) -> Optional[str]:
        if movie_fetched.rating:
            return KMDbSerializeMixin.rating_choice_map[movie_fetched.rating]

    job_choice_map = {
        {"극본": "각본", "배우": "출연"}.get(verbose, verbose): choice
        for choice, verbose in Credit.job.field.choices
    }

    cameo_type_choice_map = {
        verbose: choice for choice, verbose in Credit.cameo_type.field.choices
    }

    def serialize_credits(
        self,
        movie_fetched: MovieFromKMDb,
        filtered: Optional[bool] = None,
        partial: bool = False,
    ) -> list[SerializedCreditFromAPI]:
        _filtered = self.filtered if filtered is None else filtered
        return [
            dict(
                job=KMDbSerializeMixin.job_choice_map.get(
                    s.staffRoleGroup, s.staffRoleGroup
                ),
                role_name=s.staffRole,
                cameo_type=KMDbSerializeMixin.cameo_type_choice_map.get(s.staffEtc, "")
                if _filtered
                else s.staffEtc,
                people=dict(
                    kmdb_id=s.staffId,
                    name=s.staffNm,
                    en_name=s.staffEnNm,
                ),
            )
            for s in movie_fetched.staffs.staff
            if not _filtered
            or (
                s.staffRoleGroup in KMDbSerializeMixin.job_choice_map.keys()
                and (partial or (s.staffId and (s.staffNm or s.staffEnNm)))
            )
        ]

    def serialize_poster_set(
        self, movie_fetched: MovieFromKMDb, **kwargs
    ) -> Optional[list[dict[str, bool | str]]]:
        if movie_fetched.posters:
            return [
                {
                    "is_main": True,
                    "image_url": (posters := movie_fetched.posters.split("|"))[0],
                }
            ] + [{"is_main": False, "image_url": p} for p in posters[1:]]

    def serialize_still_set(
        self, movie_fetched: MovieFromKMDb, **kwargs
    ) -> Optional[list[dict[str, str]]]:
        if movie_fetched.stills:
            return [{"image_url": s} for s in movie_fetched.stills.split("|")]


class TMDBDetailMixin(ListAndDetailCrawler):
    tmdb_agent: TMDBAPIAgent

    def detail(self, movie: SimpleMovieFromTMDB) -> MovieFromTMDB:
        return self.tmdb_agent.movie_detail(movie.id)


class ComplementaryDetailMixin(
    TMDBSerializeMixin, KMDbSerializeMixin, ListAndDetailCrawler
):
    filtered: bool = True

    from_tmdb_fields = [
        "tmdb_id",
        "title",
        "synopsys",
        "countries",
        "poster_set",
        "still_set",
        "video_set",
    ]
    from_kmdb_fields = [
        "kmdb_id",
        "genres",
        "release_date",
        "production_year",
        "running_time",
        "film_rating",
    ]

    tmdb_agent: TMDBAPIAgent
    kmdb_agent: KMDbAPIAgent

    def detail(
        self, movie: SimpleMovieFromTMDB
    ) -> tuple[MovieFromTMDB, Optional[MovieFromKMDb]]:
        # 1. movie detail w/ TMDB API
        tmdb_movie = self.tmdb_agent.movie_detail(movie.id)

        # 2. movie detail w/ KMDb API
        if tmdb_movie.director_en_names:
            for kmdb_movie in self.kmdb_agent.search_movies(
                title=movie.title,
                director=" ".join(
                    [n.remove_accents(n.fullname) for n in tmdb_movie.director_en_names]
                ),
                listCount=5,
                max_count=10,
            ):
                if kmdb_movie == tmdb_movie:
                    return tmdb_movie, kmdb_movie

        for d in tmdb_movie.release_dates:
            for kmdb_movie in self.kmdb_agent.search_movies(
                title=movie.title,
                releaseDts=datetime.date.strftime(
                    d - datetime.timedelta(days=7), "%Y%m%d"
                ),
                releaseDte=datetime.date.strftime(
                    d + datetime.timedelta(days=7), "%Y%m%d"
                ),
                listCount=5,
                max_count=10,
            ):
                if kmdb_movie == tmdb_movie:
                    return tmdb_movie, kmdb_movie

        for kmdb_movie in self.kmdb_agent.search_movies(
            title=movie.title, listCount=30, max_count=150
        ):
            if kmdb_movie == tmdb_movie:
                return tmdb_movie, kmdb_movie

        return tmdb_movie, None

    def serialize(
        self,
        tmdb_movie_fetched: MovieFromTMDB,
        kmdb_movie_fetched: Optional[MovieFromKMDb],
        filtered: Optional[bool] = None,
    ) -> dict[str, Any]:
        if not kmdb_movie_fetched:
            movie_json = FieldLevelSerializeMixin.serialize(
                self,
                tmdb_movie_fetched,
                fields=TMDBSerializeMixin.fields_to_serialize,
                filtered=filtered,
                cls=TMDBSerializeMixin,
            )
        else:
            movie_json = {}

            for fname in self.from_tmdb_fields:
                if tmdb_serializer := getattr(
                    TMDBSerializeMixin, f"serialize_{fname}", False
                ):
                    movie_json[fname] = tmdb_serializer(
                        self, tmdb_movie_fetched, filtered=filtered
                    )
                elif kmdb_serializer := getattr(
                    KMDbSerializeMixin, f"serialize_{fname}", False
                ):
                    movie_json[fname] = kmdb_serializer(
                        self, kmdb_movie_fetched, filtered=filtered
                    )

            for fname in self.from_kmdb_fields:
                if kmdb_serializer := getattr(
                    KMDbSerializeMixin, f"serialize_{fname}", False
                ):
                    movie_json[fname] = kmdb_serializer(
                        self, kmdb_movie_fetched, filtered=filtered
                    )
                elif tmdb_serializer := getattr(
                    TMDBSerializeMixin, f"serialize_{fname}", False
                ):
                    movie_json[fname] = tmdb_serializer(
                        self, tmdb_movie_fetched, filtered=filtered
                    )

            # merge credits
            merged_credits = self.merge_credits(
                tmdb_credits=TMDBSerializeMixin.serialize_credits(
                    self, tmdb_movie_fetched, filtered=filtered
                ),
                kmdb_credits=KMDbSerializeMixin.serialize_credits(
                    self, kmdb_movie_fetched, filtered=filtered, partial=True
                ),
            )
            if filtered is True or self.filtered:
                movie_json["credits"] = self.filter_credits(merged_credits)
            else:
                movie_json["credits"] = merged_credits

        return movie_json

    def filter_credits(
        self, credits: list[SerializedCreditFromAPI]
    ) -> list[SerializedCreditFromAPI]:
        return list(
            filter(
                lambda credit: (
                    (people := credit["people"]).get("name") or people.get("en_name")
                )
                and (people.get("tmdb_id") or people.get("kmdb_id")),
                credits,
            )
        )

    def merge_credits(
        self,
        tmdb_credits: list[SerializedCreditFromAPI],
        kmdb_credits: list[SerializedCreditFromAPI],
    ) -> dict[str, Any]:
        tmdb_book = self.make_names_book(tmdb_credits)
        kmdb_book = self.make_names_book(kmdb_credits)

        merged = []
        for job, tmdb_credits_by_name in tmdb_book.items():
            names_marked = set()
            kmdb_credits_by_name = kmdb_book.get(job, {})
            for (
                t_name,
                t_en_name,
            ), tmdb_credits_ in tmdb_credits_by_name.items():
                if not (t_names := {t_name, t_en_name}) & names_marked:
                    names_marked |= t_names

                    kmdb_credits_ = []
                    for k_names in [
                        (k_name, k_en_name)
                        for k_name, k_en_name in kmdb_credits_by_name.keys()
                        if (t_name and k_name and t_name == k_name)
                        or (t_en_name and k_en_name and t_en_name == k_en_name)
                    ]:
                        names_marked |= set(k_names)
                        kmdb_credits_ += kmdb_credits_by_name.pop(k_names)

                    if len(tmdb_credits_) == len(kmdb_credits_) == 1:
                        tmdb_credit = tmdb_credits_[0]
                        kmdb_credit = kmdb_credits_[0]
                        merged.append(
                            {
                                "job": tmdb_credit["job"],
                                "role_name": kmdb_credit.get("role_name")
                                or tmdb_credit.get("role_name", ""),
                                "cameo_type": kmdb_credit.get("cameo_type", ""),
                                "people": kmdb_credits_[0]["people"]
                                | tmdb_credits_[0]["people"],
                            }
                        )
                    else:
                        merged += (
                            tmdb_credits_
                            if len(tmdb_credits_) >= len(kmdb_credits_)
                            else kmdb_credits_
                        )
            for (k_name, k_en_name), kmdb_credits_ in kmdb_credits_by_name.items():
                if not (k_names := {k_name, k_en_name}) & names_marked:
                    names_marked |= k_names
                    merged += kmdb_credits_

        return merged

    def make_names_book(
        self, credits: list[SerializedCreditFromAPI]
    ) -> DefaultDict[
        str, DefaultDict[tuple[str, EnglishName], list[SerializedCreditFromAPI]]
    ]:
        book = defaultdict(lambda: defaultdict(list))
        for c in credits:
            book[c["job"]][
                (
                    validate_kmdb_text(c["people"].get("name", "")),
                    EnglishName(validate_kmdb_text(c["people"].get("en_name", ""))),
                )
            ].append(c)
        return book

    def run(
        self, filtered: Optional[bool] = None, *args, **kwargs
    ) -> list[Movie | MovieFromAPISerializer]:
        """
        Total process of fetch -> serialize -> register steps of crawling movies from API
        """
        return [
            self.register(self.serialize(tmdb_movie, kmdb_movie, filtered=filtered))
            for tmdb_movie, kmdb_movie in self.fetch(*args, **kwargs)
        ]


class TMDBAgentInitMixin:
    def __init__(self, *, tmdb_api_token: str, **kwargs):
        self.tmdb_agent = TMDBAPIAgent(access_token=tmdb_api_token)
        super().__init__(**kwargs)


class KMDbAgentInitMixin:
    def __init__(self, *, kmdb_api_key: str, **kwargs):
        self.kmdb_agent = KMDbAPIAgent(api_key=kmdb_api_key)
        super().__init__(**kwargs)
