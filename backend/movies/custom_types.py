from __future__ import annotations

from dataclasses import field
from typing import Optional

from .decorators import flexible_dataclass
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
    name: str


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


@flexible_dataclass
class StaffFromKMDb(EmptyStringToNoneMixin):
    staffId: str
    staffNm: str
    staffEnNm: str
    staffRoleGroup: str
    staffRole: Optional[str] = None


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
    titleEng: Optional[str] = None
    titleOrg: Optional[str] = None
    repRlsDate: Optional[str] = None
    runtime: Optional[str] = None
    genre: Optional[str] = None
    plot: Optional[str] = None
    rating: Optional[str] = None
    posters: Optional[str] = None
    stills: Optional[str] = None
