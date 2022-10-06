from .mixins.crawler import (
    ComplementaryDetailMixin,
    KMDbAgentInitMixin,
    PopularListMixin,
    TMDBAgentInitMixin,
    TMDBDetailMixin,
    TMDBSerializeMixin,
    TopRatedListMixin,
    TrendingListMixin,
)


class TopRatedComplementaryMovieAPICrawler(
    TMDBAgentInitMixin, KMDbAgentInitMixin, ComplementaryDetailMixin, TopRatedListMixin
):
    pass


class TopRatedTMDBMovieAPICrawler(
    TMDBAgentInitMixin, TMDBSerializeMixin, TMDBDetailMixin, TopRatedListMixin
):
    pass


class PopularComplementaryMovieAPICrawler(
    TMDBAgentInitMixin, KMDbAgentInitMixin, ComplementaryDetailMixin, PopularListMixin
):
    pass


class PopularTMDBMovieAPICrawler(
    TMDBAgentInitMixin, TMDBSerializeMixin, TMDBDetailMixin, PopularListMixin
):
    pass


class TrendingComplementaryMovieAPICrawler(
    TMDBAgentInitMixin, KMDbAgentInitMixin, ComplementaryDetailMixin, TrendingListMixin
):
    pass


class TrendingTMDBMovieAPICrawler(
    TMDBAgentInitMixin, TMDBSerializeMixin, TMDBDetailMixin, TrendingListMixin
):
    pass
