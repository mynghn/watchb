from __future__ import annotations

import os
from typing import Any, Dict, List, Literal, Optional, Tuple
from urllib.parse import parse_qs, urlparse

import requests

from . import custom_types as T
from .decorators import lazy_load_property
from .mixins.api import RequestPaginateMixin, SingletonRequestSessionMixin


class TMDBAPIAgent(RequestPaginateMixin, SingletonRequestSessionMixin):
    base_url = os.getenv(
        "TMDB_API_BASE_URL",
        "https://api.themoviedb.org/3",
    ).rstrip("/")

    def __init__(self, access_token: str, language: str = "ko", region: str = "KR"):
        self.session.headers.update({"Authorization": f"Bearer {access_token}"})
        self.session.params.update({"language": language, "region": region})

    def request_page(
        self,
        method: str,
        url: str,
        params: Dict[str, Any] = {},
        former_response: Optional[requests.Response] = None,
        **kwargs,
    ) -> requests.Response:
        if former_response:
            params.update({"page": former_response.json().get("page", 0) + 1})
        else:
            params.update({"page": 1})

        return self.session.request(method, url, params, **kwargs)

    def process_response(
        self, response: requests.Response, **kwargs
    ) -> Tuple[List[Dict[str, Any]], bool]:
        response_json: dict = response.json()

        # 1. instances
        instances = response_json.get("results", [])

        # 2. has_next
        curr_page = response_json.get("page")
        total_pages = response_json.get("total_pages")
        has_next = (curr_page and total_pages) and (curr_page < total_pages)

        return instances, has_next

    def popular_movies(
        self, max_count: Optional[int] = None
    ) -> List[T.SimpleMovieFromTMDB]:
        method = "GET"
        uri = "/movie/popular"

        return [
            T.SimpleMovieFromTMDB(**m)
            for m in self.paginate(method, self.base_url + uri, max_count=max_count)
        ]

    def top_rated_movies(
        self, max_count: Optional[int] = None
    ) -> List[T.SimpleMovieFromTMDB]:
        method = "GET"
        uri = "/movie/top_rated"

        return [
            T.SimpleMovieFromTMDB(**m)
            for m in self.paginate(method, self.base_url + uri, max_count=max_count)
        ]

    def now_playing_movies(
        self, max_count: Optional[int] = None
    ) -> List[T.SimpleMovieFromTMDB]:
        method = "GET"
        uri = "/movie/now_playing"

        return [
            T.SimpleMovieFromTMDB(**m)
            for m in self.paginate(method, self.base_url + uri, max_count=max_count)
        ]

    def trending_movies(
        self, time_window: Literal["day", "week"], max_count: Optional[int] = None
    ) -> List[T.SimpleMovieFromTMDB]:
        method = "GET"
        uri = f"/trending/movie/{time_window}"

        return [
            T.SimpleMovieFromTMDB(**m)
            for m in self.paginate(method, self.base_url + uri, max_count=max_count)
        ]

    def search_movies(
        self, query: str, year: Optional[int] = None, max_count: Optional[int] = None
    ) -> List[T.SimpleMovieFromTMDB]:
        method = "GET"
        uri = "/search/movie"
        params = {"query": query, "year": year, "include_adult": False}

        return [
            T.SimpleMovieFromTMDB(**m)
            for m in self.paginate(
                method, self.base_url + uri, params=params, max_count=max_count
            )
        ]

    def movie_detail(self, movie_id: int) -> T.MovieFromTMDB:
        method = "GET"
        uri = f"/movie/{movie_id}"
        params = {
            "append_to_response": "images,videos",
            "include_image_language": "ko,null",
            "include_video_language": "ko,null",
        }

        return T.MovieFromTMDB(
            **self.session.request(method, self.base_url + uri, params).json(),
            credits=self.movie_credits(movie_id),
            kr_release_dates=self.movie_kr_release_dates(movie_id),
        )

    def movie_kr_release_dates(self, movie_id: int) -> list[dict[str, str | int]]:
        method = "GET"
        uri = f"/movie/{movie_id}/release_dates"
        KOREA_REGION = "KR"

        response = self.session.request(method, self.base_url + uri).json()

        for r in response.get("results", []):
            if r.get("iso_3166_1") == KOREA_REGION:
                return r.get("release_dates", [])
        return []

    def movie_credits(self, movie_id: int) -> T.MovieCreditsFromTMDB:
        method = "GET"
        uri = f"/movie/{movie_id}/credits"

        response = self.session.request(method, self.base_url + uri).json()

        return T.MovieCreditsFromTMDB(**response)

    def person_detail(self, person_id: int) -> T.PeopleFromTMDB:
        method = "GET"
        uri = f"/person/{person_id}"
        params = {"append_to_response": "images", "include_image_language": "ko,null"}

        return T.PeopleFromTMDB(
            **self.session.request(method, self.base_url + uri, params).json()
        )

    @lazy_load_property
    def image_base_url(self) -> str:
        uri = "/configuration"
        IMG_CONFIGS_KEY = "images"
        IMG_BASE_URL_KEY = "secure_base_url"

        response = self.session.get(self.base_url + uri).json()
        if not (configs := response.get(IMG_CONFIGS_KEY)):
            raise KeyError(f"Can't find '{IMG_CONFIGS_KEY}' key in {uri} API response")
        else:
            if not (base_url := configs.get(IMG_BASE_URL_KEY)):
                raise KeyError(
                    f"Can't find '{IMG_BASE_URL_KEY}' key in '{IMG_CONFIGS_KEY}' json object in {uri} API response"
                )
            else:
                return base_url.rstrip("/") + "/original"


class KMDbAPIAgent(RequestPaginateMixin, SingletonRequestSessionMixin):
    base_url = os.getenv(
        "KMDB_API_BASE_URL",
        "http://api.koreafilm.or.kr/openapi-data2/wisenut",
    ).rstrip("/")

    def __init__(self, api_key: str):
        self.session.params.update({"collection": "kmdb_new2", "ServiceKey": api_key})

    def request_page(
        self,
        method: str,
        url: str,
        params: Dict[str, Any],
        former_response: Optional[requests.Response] = None,
        **kwargs,
    ) -> requests.Response:
        if former_response:
            former_start = int(
                parse_qs(urlparse(former_response.url).query).get("startCount", [0])[0]
            )
            former_data = former_response.json().get("Data", [{}])[0]
            former_count = former_data.get("Count") or len(
                former_data.get("Result", [])
            )
            params.update({"startCount": former_start + former_count})
        else:
            params.update({"startCount": 0})

        return self.session.request(method, url, params, **kwargs)

    def process_response(
        self, response: requests.Response, **kwargs
    ) -> Tuple[List[Dict[str, Any]], bool]:
        response_json = response.json()

        # 1. instances
        instances = response_json.get("Data", [{}])[0].get("Result", [])

        # 2. has_next
        total_count = response_json.get("TotalCount")
        curr_start = int(
            parse_qs(urlparse(response.url).query).get("startCount", [0])[0]
        )
        curr_count = len(instances)
        has_next = total_count and (curr_start + 1 + curr_count < total_count)

        return instances, has_next

    def search_movies(
        self, max_count: Optional[int] = None, **search_kwargs
    ) -> List[T.MovieFromKMDb]:
        method = "GET"
        uri = "/search_api/search_json2.jsp"

        return [
            T.MovieFromKMDb(**m)
            for m in self.paginate(
                method, self.base_url + uri, params=search_kwargs, max_count=max_count
            )
        ]
