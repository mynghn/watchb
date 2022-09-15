from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Any, Type

from rest_framework.serializers import ModelSerializer

from ..custom_types import MovieFromAPI
from ..models import Movie
from ..serializers import MovieFromAPISerializer


class APICrawler(metaclass=ABCMeta):
    serializer_class: Type[ModelSerializer] = MovieFromAPISerializer

    @abstractmethod
    def fetch(self, *args, **kwargs) -> list[MovieFromAPI]:
        """
        Fetch movies data from API
        """
        raise NotImplementedError

    @abstractmethod
    def serialize(self, movie_fetched: MovieFromAPI) -> dict[str, Any]:
        """
        Serialize the movie fetched from API to JSON (w/o any validation)
        """
        raise NotImplementedError

    def register(self, movie_data: dict[str, Any]) -> Movie | MovieFromAPISerializer:
        """
        Save API fetched & serialized movie to DB w/ DRF Serializer (perform all validations here)
        """
        serializer = self.serializer_class(data=movie_data)
        if serializer.is_valid():
            return serializer.save()
        else:
            return serializer

    def run(self, *args, **kwargs) -> list[Movie | MovieFromAPISerializer]:
        """
        Total process of fetch -> serialize -> register steps of crawling movies from API
        """
        return [
            self.register(self.serialize(fetched))
            for fetched in self.fetch(*args, **kwargs)
        ]
