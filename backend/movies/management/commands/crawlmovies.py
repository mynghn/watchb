import os
from argparse import BooleanOptionalAction

from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.forms.models import model_to_dict

from ...mixins import crawler as crawler_mixins
from ...models import Movie


class Command(BaseCommand):
    help = "Crawl movies from API and register in database."

    def add_arguments(self, parser: CommandParser):
        # define crawler
        parser.add_argument(
            "-lm",
            "--list-method",
            choices=["TopRated", "Popular", "Trending", "NowPlaying", "Search"],
            required=True,
            help="choose method for first fetching movie lists",
        )
        parser.add_argument(
            "-dm",
            "--detail-method",
            choices=["Complementary", "TMDB"],
            required=True,
            help="choose method for second filling in each movie details",
        )

        # crawler init kwargs
        parser.add_argument("--tmdb-token", help="JWT string for TMDB API call")
        parser.add_argument(
            "--kmdb-key",
            help="API key for KMDb API call (needed when using Complementary detail method)",
        )

        # crawler run kwargs
        parser.add_argument(
            "-c",
            "--max-count",
            type=int,
            help="max number to fetch when first listing movies from TMDB API",
        )
        parser.add_argument(
            "-w",
            "--time-window",
            choices=["day", "week"],
            default="week",
            help="set time window when using Trending list method",
        )
        parser.add_argument("-q", "--query", help="query for Search list method")
        parser.add_argument(
            "-y", "--year", type=int, help="year to query when using Search list method"
        )

        # debug option
        parser.add_argument(
            "--debug",
            action=BooleanOptionalAction,
            default=False,
            help="choose whether to present detailed crawling results",
        )

    def handle(self, *args, **options):
        if tmdb_api_token := options["tmdb_token"] or os.getenv("TMDB_API_TOKEN"):
            init_kwargs = {"tmdb_api_token": tmdb_api_token}
        else:
            raise CommandError(
                "You should either pass TMDB API token from CLI with '-tmdb--token' kwarg "
                "or set 'TMDB_API_TOKEN' environment variable."
            )

        if options["detail_method"] == "Complementary":
            if kmdb_api_key := options["kmdb_key"] or os.getenv("KMDB_API_KEY"):
                init_kwargs["kmdb_api_key"] = kmdb_api_key
            else:
                raise CommandError(
                    "You should either pass KMDb API key from CLI with '-kmdb--key' kwarg "
                    "or set 'KMDB_API_KEY' environment variable "
                    "when using 'Complementary' deatil method."
                )

            mixins = [
                crawler_mixins.TMDBAgentInitMixin,
                crawler_mixins.KMDbAgentInitMixin,
                getattr(crawler_mixins, f"{options['detail_method']}DetailMixin"),
                getattr(crawler_mixins, f"{options['list_method']}ListMixin"),
            ]
        elif options["detail_method"] == "TMDB":
            mixins = [
                crawler_mixins.TMDBAgentInitMixin,
                crawler_mixins.TMDBSerializeMixin,
                getattr(crawler_mixins, f"{options['detail_method']}DetailMixin"),
                getattr(crawler_mixins, f"{options['list_method']}ListMixin"),
            ]

        run_kwargs = {}
        if options["max_count"]:
            run_kwargs["max_count"] = options["max_count"]

        if options["list_method"] == "Search":
            if options["query"]:
                run_kwargs["query"] = options["query"]
            else:
                raise CommandError(
                    "You should pass query to search when using 'Search' list method."
                )
            if options["year"]:
                run_kwargs["year"] = options["year"]
        elif options["list_method"] == "Trending":
            run_kwargs["time_window"] = options["time_window"]
        else:
            run_kwargs = {"max_count": options["max_count"]}

        class Crawler(*mixins):
            debug = options["debug"]

        crawler = Crawler(**init_kwargs)

        result = crawler.run(**run_kwargs)
        success = [
            (m, s)
            for m, s in result
            if isinstance(m, Movie) and isinstance(s, Crawler.serializer_class)
        ]
        existed = [r for r in result if r[1] is None]

        self.stdout.write("\n")
        self.stdout.write(self.style.HTTP_SUCCESS(f"Crawled: {(n_total:=len(result))}"))
        self.stdout.write(
            self.style.SUCCESS(f"Registered: {(n_success:=len(success))}")
        )
        self.stdout.write(f"Pre-existed: {(n_existed:=len(existed))}")

        if options["debug"]:
            # SUCESS
            self.stdout.write("\n")
            self.stdout.write(
                self.style.SUCCESS(
                    f"==================== SUCCESS: {n_success} ===================="
                )
            )
            for m, s in success:
                self.stdout.write(
                    self.style.SUCCESS(
                        model_to_dict(m, fields=["id", "tmdb_id", "kmdb_id", "title"])
                    ),
                )
                if skipped_errors := getattr(self, "skipped_errors", False):
                    self.stdout.write(
                        self.style.WARNING(f"Skipped errors:\t{skipped_errors}")
                    )
                self.stdout.write("\n")
            if any(not m for m, _ in result):
                # FAILURE
                self.stdout.write("\n")
                self.stdout.write(
                    self.style.ERROR(
                        f"==================== FAILURE: {n_total - n_existed - n_success} ===================="
                    )
                )
                for m, s in result:
                    if not m:
                        self.stdout.write(
                            repr(
                                {
                                    "tmdb_id": s.initial_data.get("tmdb_id", "empty"),
                                    "kmdb_id": s.initial_data.get("kmdb_id", "empty"),
                                }
                            )
                        )
                        self.stdout.write(
                            self.style.ERROR_OUTPUT(f"Errors:\t{s.errors}")
                        )
                        self.stdout.write("\n")
                        self.stdout.write(
                            self.style.WARNING(
                                f"Initial data:\t{dict((k,s.initial_data[k]) for k in s.errors.keys())}"
                            )
                        )
