from abc import ABCMeta, abstractmethod
from typing import Any, Type

import requests
from bs4 import BeautifulSoup
from rest_framework.serializers import ModelSerializer

from movies.serializers import MovieRegisterSerializer

from .custom_types import MovieFromAPI
from .models import Movie


class MovieAPICrawler(metaclass=ABCMeta):
    serializer_class: Type[ModelSerializer] = MovieRegisterSerializer

    @abstractmethod
    def fetch(self, *args, **kwargs) -> list[MovieFromAPI]:
        """
        Fetch movies data from API
        """
        raise NotImplementedError

    @abstractmethod
    def serialize(self, movie_fetched: MovieFromAPI) -> dict[str, Any]:
        """
        Serialize the movie fetched from API to JSON
        """
        raise NotImplementedError

    def register(self, movie_data: dict[str, Any]) -> Movie:
        """
        Save API fetched & serialized movie to DB w/ DRF Serializer
        """
        serializer = self.serializer_class(data=movie_data)
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    @abstractmethod
    def run(self, *args, **kwargs) -> list[Movie]:
        """
        Total process of fetch -> serialize -> register steps of crawling movies from API
        """
        raise NotImplementedError


class CountryCrawler:
    url = "https://ko.wikipedia.org/wiki/ISO_3166-1"
    _book = {}

    @classmethod
    def _set_countries(cls):
        response = requests.get(cls.url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.table.findChildren("tr")
        keys = [header.text.rstrip() for header in rows.pop(0).findChildren("th")]

        for row in rows:
            country = {}
            for idx, cell in enumerate(row.findChildren("td")):
                country[keys[idx]] = cell.text.strip().upper()
            for v in country.values():
                cls._book[v] = country

    @classmethod
    def get_country(cls, key: str) -> dict[str, str]:
        if not cls._book:
            cls._set_countries()

        return cls._book.get(key.upper(), {})
