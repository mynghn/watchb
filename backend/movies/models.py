from django.db import models


class Movie(models.Model):
    tmdb_id = models.IntegerField(unique=True, null=True, blank=True)
    kmdb_id = models.CharField(max_length=7, unique=True, null=True, blank=True)

    title = models.CharField(max_length=200)
    release_date = models.DateField(null=True, blank=True)
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

    staffs = models.ManyToManyField("People", through="Credit")


class People(models.Model):
    tmdb_id = models.IntegerField(unique=True, null=True, blank=True)
    kmdb_id = models.CharField(max_length=8, unique=True, null=True, blank=True)

    name = models.CharField(max_length=50)
    biography = models.TextField(blank=True)
    avatar_url = models.URLField(blank=True, unique=True)


class Credit(models.Model):
    DIRECTOR = ("director", "감독")
    WRITER = ("writer", "극본")
    ACTOR = ("actor", "배우")
    JOB_CHOICES = [DIRECTOR, WRITER, ACTOR]
    job = models.CharField(max_length=8, choices=JOB_CHOICES)

    role_name = models.CharField(max_length=50, blank=True)  # for actors
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="credits")
    people = models.ForeignKey(
        People, on_delete=models.CASCADE, related_name="filmography"
    )


class Country(models.Model):
    # follows ISO 3166-1
    alpha_2 = models.CharField(max_length=2, primary_key=True)
    name = models.CharField(max_length=50)


class Genre(models.Model):
    # from KMDb genre list
    name = models.CharField(max_length=7, unique=True)


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
    title = models.CharField(max_length=50, null=True)
    youtube_id = models.CharField(max_length=11)

    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["movie", "title"], name="unique_title_in_movie"
            ),
            models.UniqueConstraint(
                fields=["movie", "youtube_id"], name="unique_video_in_movie"
            ),
        ]
