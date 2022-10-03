from abstract_models import CreateAndUpdateModel, TimestampModel
from django.contrib.auth import get_user_model
from django.db import models


class Movie(models.Model):
    tmdb_id = models.IntegerField(unique=True, null=True, blank=True)
    kmdb_id = models.CharField(max_length=7, unique=True, null=True, blank=True)

    title = models.CharField(max_length=50)
    release_date = models.DateField(null=True, blank=True)
    production_year = models.IntegerField(null=True, blank=True)
    countries = models.ManyToManyField("Country", blank=True)
    genres = models.ManyToManyField("Genre", blank=True)
    running_time = models.DurationField(null=True, blank=True)
    synopsys = models.TextField(blank=True)

    ALL_AGE = ("ALL", "전체관람가")
    OVER_12 = ("12", "12세이상관람가")
    OVER_15 = ("15", "15세이상관람가")
    OVER_18 = ("18", "청소년관람불가")
    RESTRICTED = ("R18", "제한상영가")
    FILM_RATING_CHOICES = [ALL_AGE, OVER_12, OVER_15, OVER_18, RESTRICTED]
    film_rating = models.CharField(
        max_length=3, choices=FILM_RATING_CHOICES, blank=True
    )

    people = models.ManyToManyField("Person", through="Credit")


class Person(models.Model):
    tmdb_id = models.IntegerField(unique=True, null=True, blank=True)
    kmdb_id = models.CharField(max_length=8, unique=True, null=True, blank=True)

    name = models.CharField(max_length=30, blank=True)
    en_name = models.CharField(max_length=50, blank=True)
    biography = models.TextField(blank=True)
    avatar_url = models.URLField(blank=True, null=True, unique=True)


class Credit(models.Model):
    DIRECTOR = ("director", "감독")
    WRITER = ("writer", "극본")
    ACTOR = ("actor", "배우")
    JOB_CHOICES = [DIRECTOR, WRITER, ACTOR]
    job = models.CharField(max_length=8, choices=JOB_CHOICES)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="credits")
    person = models.ForeignKey(
        Person, on_delete=models.CASCADE, related_name="filmography"
    )

    # for actors
    SPECIAL = ("special", "특별출연")
    FRIEND = ("friend", "우정출연")
    CAMEO_CHOICES = [SPECIAL, WRITER, FRIEND]
    cameo_type = models.CharField(max_length=7, choices=CAMEO_CHOICES, blank=True)
    role_name = models.CharField(max_length=200, blank=True)


class Country(models.Model):
    # follows ISO 3166-1
    alpha_2 = models.CharField(max_length=2, primary_key=True)
    name = models.CharField(max_length=17, unique=True)


class Genre(models.Model):
    # from KMDb genre list
    name = models.CharField(max_length=10, unique=True)


class MovieImage(models.Model):
    image_url = models.URLField()

    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class Poster(MovieImage):
    is_main = models.BooleanField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["movie", "image_url"], name="unique_poster_in_movie"
            )
        ]


class Still(MovieImage):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["movie", "image_url"], name="unique_still_in_movie"
            )
        ]


class Video(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True)

    VIDEO_SITE_CHOICES = [("youtube", "YouTube")]
    site = models.CharField(max_length=7, choices=VIDEO_SITE_CHOICES)
    external_id = models.CharField(max_length=11)

    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["movie", "title"], name="unique_title_in_movie"
            ),
            models.UniqueConstraint(
                fields=["movie", "site", "external_id"], name="unique_video_in_movie"
            ),
        ]


User = get_user_model()


class Rating(CreateAndUpdateModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ratings")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="ratings")
    score = models.FloatField(choices=[(n / 2, str(n / 2)) for n in range(11)])

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "movie"], name="one_rating_per_user_movie"
            )
        ]


class Review(CreateAndUpdateModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="reviews")
    comment = models.TextField()
    has_spoiler = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "movie"], name="one_review_per_user_movie"
            )
        ]


class Wishlist(TimestampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlists")
    movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE, related_name="wishlisted"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "movie"], name="one_wishlist_per_user_movie"
            )
        ]


class Blocklist(TimestampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocklists")
    movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE, related_name="blocklisted"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "movie"], name="one_blocklist_per_user_movie"
            )
        ]


class ReviewLike(TimestampModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="review_likes"
    )
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="liked")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "review"], name="one_like_per_user_review"
            )
        ]


class PersonLike(TimestampModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="person_likes"
    )
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="liked")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "person"], name="one_like_per_user_person"
            )
        ]
