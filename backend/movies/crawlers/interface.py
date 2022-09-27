from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Any, Optional, Type

from rest_framework.serializers import ModelSerializer
from tqdm import tqdm

from ..custom_types import MovieFromAPI, SimpleMovieFromTMDB
from ..models import Movie
from ..serializers import MovieFromAPISerializer


class APICrawler(metaclass=ABCMeta):
    serializer_class: Type[ModelSerializer] = MovieFromAPISerializer
    debug: bool = False

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

    def get_or_register(
        self, movie_data: dict[str, Any]
    ) -> tuple[Optional[Movie], Optional[MovieFromAPISerializer]]:
        """
        Save API fetched & serialized movie to DB w/ DRF Serializer (perform all validations here)
        """
        if (
            (tmdb_id := movie_data.get("tmdb_id"))
            and (movie_filtered := Movie.objects.filter(tmdb_id=tmdb_id))
        ) or (
            (kmdb_id := movie_data.get("kmdb_id"))
            and (movie_filtered := Movie.objects.filter(kmdb_id=kmdb_id))
        ):
            return movie_filtered.get(), None
        else:
            serializer = self.serializer_class(data=movie_data)
            if serializer.is_valid():
                return serializer.save(), serializer
            else:
                return None, serializer

    def run(
        self, *args, **kwargs
    ) -> list[tuple[Optional[Movie], Optional[MovieFromAPISerializer]]]:
        """
        Total process of fetch -> serialize -> register steps of crawling movies from API
        """
        if self.debug:
            movies_fetched = tqdm(
                self.fetch(*args, **kwargs),
                desc="serialize and registering for each movie fetched...",
            )
        else:
            movies_fetched = self.fetch(*args, **kwargs)
        return [
            self.get_or_register(self.serialize(fetched)) for fetched in movies_fetched
        ]


class ListAndDetailCrawler(APICrawler):
    @abstractmethod
    def list(self, *args, **kwargs) -> list[SimpleMovieFromTMDB]:
        raise NotImplementedError

    @abstractmethod
    def get_or_detail(self, movie: SimpleMovieFromTMDB) -> MovieFromAPI:
        raise NotImplementedError

    def fetch(self, *args, **kwargs) -> list[SimpleMovieFromTMDB]:
        return self.list(*args, **kwargs)

    def run(
        self, *args, **kwargs
    ) -> list[tuple[Optional[Movie], Optional[MovieFromAPISerializer]]]:
        """
        Total process of fetch -> serialize -> register steps of crawling movies from API
        """
        if self.debug:
            listed = tqdm(
                self.list(*args, **kwargs),
                desc="detail -> serialize -> register for each movie listed...",
            )
        else:
            listed = self.list(*args, **kwargs)

        return [
            (movie_detailed, None)
            if isinstance(movie_detailed := self.get_or_detail(m), Movie)
            else self.get_or_register(self.serialize(movie_detailed))
            for m in listed
        ]
