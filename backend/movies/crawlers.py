from abc import ABCMeta, abstractmethod
from typing import Any, Type

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
