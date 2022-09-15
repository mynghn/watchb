from __future__ import annotations

import datetime
import re
import unicodedata
from dataclasses import field
from typing import Optional

from movies.validators import validate_kmdb_text

from .decorators import flexible_dataclass, lazy_load_property
from .mixins.dataclass import EmptyStringToNoneMixin, NestedInitMixin


@flexible_dataclass
class ImageFromTMDB:
    file_path: str
    vote_count: int
    iso_639_1: Optional[str] = None
    vote_average: Optional[float] = None

    def __post_init__(self):
        if self.vote_count == 0:
            self.vote_average = None


@flexible_dataclass
class VideoFromTMDB(EmptyStringToNoneMixin):
    site: str
    key: str
    name: Optional[str] = None
    published_at: Optional[str] = None
    iso_639_1: Optional[str] = None


@flexible_dataclass
class CountryFromTMDB:
    iso_3166_1: str


@flexible_dataclass
class PeopleImagesFromTMDB(NestedInitMixin):
    profiles: list[ImageFromTMDB]


@flexible_dataclass
class PeopleFromTMDB(NestedInitMixin, EmptyStringToNoneMixin):
    id: int
    name: str
    also_known_as: list[str]
    images: PeopleImagesFromTMDB
    biography: Optional[str] = None
    profile_path: Optional[str] = None


@flexible_dataclass
class CastFromTMDB(EmptyStringToNoneMixin):
    id: int  # people_id
    name: str
    character: Optional[str] = None


@flexible_dataclass
class CrewFromTMDB(EmptyStringToNoneMixin):
    id: int  # people_id
    name: str
    job: str


@flexible_dataclass
class MovieCreditsFromTMDB(NestedInitMixin):
    cast: list[CastFromTMDB]
    crew: list[CrewFromTMDB]


@flexible_dataclass
class MovieImagesFromTMDB(NestedInitMixin):
    posters: list[ImageFromTMDB]
    backdrops: list[ImageFromTMDB]


@flexible_dataclass
class MovieVideosFromTMDB(NestedInitMixin):
    results: list[VideoFromTMDB]


@flexible_dataclass
class ReleaseDateFromTMDB:
    type: int
    release_date: str


@flexible_dataclass
class GenreFromTMDB:
    id: int
    name: str


@flexible_dataclass
class SimpleMovieFromTMDB:
    id: int
    title: str


@flexible_dataclass
class MovieFromTMDB(NestedInitMixin, EmptyStringToNoneMixin):
    id: int
    title: str
    genres: list[GenreFromTMDB]
    production_countries: list[CountryFromTMDB]
    images: MovieImagesFromTMDB
    videos: MovieVideosFromTMDB
    credits: MovieCreditsFromTMDB
    kr_release_dates: list[ReleaseDateFromTMDB]
    original_title: Optional[str] = None
    runtime: Optional[int] = None
    overview: Optional[str] = None

    @lazy_load_property
    def director_en_names(self) -> set[EnglishName]:
        return {
            EnglishName(_crew.name)
            for _crew in self.credits.crew
            if _crew.job == "Director" and _crew.name
        }

    @lazy_load_property
    def release_dates(self) -> list[datetime.date]:
        _release_dates = []
        if self.kr_release_dates:
            for d in self.kr_release_dates:
                if d.release_date.endswith("Z"):
                    _release_date = d.release_date[:-1] + "+00:00"
                else:
                    _release_date = d.release_date
                _release_dates.append(
                    datetime.datetime.fromisoformat(_release_date).date()
                )
        return _release_dates

    def __eq__(self, kmdb_movie: MovieFromKMDb) -> bool:
        return kmdb_movie.__eq__(self)


@flexible_dataclass
class StaffFromKMDb(EmptyStringToNoneMixin):
    staffRoleGroup: str
    staffNm: str = ""
    staffEnNm: str = ""
    staffRole: str = ""
    staffEtc: str = ""
    staffId: Optional[str] = None


@flexible_dataclass
class MovieStaffsFromKMDb(NestedInitMixin):
    staff: list[StaffFromKMDb] = field(default_factory=list)


@flexible_dataclass
class PlotFromKMDb(EmptyStringToNoneMixin):
    plotLang: str
    plotText: Optional[str] = None


@flexible_dataclass
class MoviePlotsFromKMDb:
    plot: list[PlotFromKMDb] = field(default_factory=list)


@flexible_dataclass
class MovieFromKMDb(NestedInitMixin, EmptyStringToNoneMixin):
    movieId: str
    movieSeq: str
    title: str
    staffs: MovieStaffsFromKMDb
    plots: MoviePlotsFromKMDb
    nation: Optional[str] = None
    prodYear: Optional[str] = None
    titleEng: Optional[str] = None
    titleOrg: Optional[str] = None
    repRlsDate: Optional[str] = None
    runtime: Optional[str] = None
    genre: Optional[str] = None
    rating: Optional[str] = None
    posters: Optional[str] = None
    stills: Optional[str] = None

    @lazy_load_property
    def director_en_names(self) -> set[EnglishName]:
        return {
            EnglishName(validate_kmdb_text(s.staffEnNm))
            for s in self.staffs.staff
            if s.staffRoleGroup == "감독" and s.staffEnNm
        }

    @lazy_load_property
    def release_date(self) -> Optional[datetime.date]:
        if self.repRlsDate:
            try:
                return datetime.datetime.strptime(self.repRlsDate, "%Y%m%d").date()
            except ValueError as e:
                if not re.match(
                    r"^time data '[^']+' does not match format$", e.args[0]
                ):
                    raise e

    def normalize_title(self, title: str) -> str:
        return re.sub(r"[^\w]|[_]", "", validate_kmdb_text(title))

    def __eq__(self, tmdb_movie: MovieFromTMDB) -> bool:
        assert isinstance(tmdb_movie, MovieFromTMDB)
        title_check = self._title_check(tmdb_movie.title, tmdb_movie.original_title)
        directors_check = self._directors_check(tmdb_movie.director_en_names)
        release_date_check = self._release_date_check(
            tmdb_movie.release_dates, margin=7
        )
        runtime_check = self._runtime_check(tmdb_movie.runtime, margin=5)

        is_equal = (
            title_check and (directors_check is True) or (release_date_check is True)
        ) or (
            directors_check is True
            and release_date_check is True
            and runtime_check is True
        )

        return is_equal

    def _title_check(self, *tmdb: tuple[Optional[str], ...]) -> bool:
        def normalized_title_set(*titles: tuple[Optional[str]]) -> set[str]:
            return set(map(self.normalize_title, filter(None, titles)))

        return bool(
            normalized_title_set(self.title, self.titleEng, self.titleOrg)
            & normalized_title_set(*tmdb)
        )

    def _directors_check(self, tmdb: set[EnglishName]) -> Optional[bool]:
        if self.director_en_names and tmdb:
            return self.director_en_names.issubset(tmdb) or tmdb.issubset(
                self.director_en_names
            )

    def _release_date_check(
        self, tmdb: list[datetime.date], margin: int
    ) -> Optional[bool]:
        if self.release_date and tmdb:
            return any([abs((self.release_date - d).days) <= margin for d in tmdb])

    def _runtime_check(self, tmdb: int, margin: int) -> Optional[bool]:
        if self.runtime and tmdb:
            return abs(int(self.runtime) - tmdb) <= margin


MovieFromAPI = MovieFromTMDB | MovieFromKMDb


class EnglishName(str):
    fullname: str

    def __init__(self, fullname: str):
        self.fullname = fullname

    @classmethod
    def remove_accents(self, name: str) -> str:
        return unicodedata.normalize("NFD", name).encode("ascii", "ignore").decode()

    @classmethod
    def remove_hyphens(self, name: str) -> str:
        return name.replace("-", "")

    @property
    def normalized(self):
        return self.remove_accents(self.remove_hyphens(self.fullname)).lower()

    def __eq__(self, another: EnglishName | str) -> bool:
        if isinstance(another, EnglishName):
            return self.normalized == another.normalized
        elif isinstance(another, str):
            return self.fullname == another
        else:
            raise TypeError(f"comparison unable with type {type(another)}")

    def __hash__(self):
        return self.normalized.__hash__()


SerializedPeopleFromAPI = dict[str, int | str | None]


SerializedCreditFromAPI = dict[str, str | SerializedPeopleFromAPI]
