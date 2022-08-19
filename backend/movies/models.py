from django.db import models


class Movie(models.Model):
    title = models.CharField(max_length=200)
    release_date = models.DateField()
    countries = models.ManyToManyField("Country")
    genres = models.ManyToManyField("Genre")
    running_time = models.DurationField()

    ALL_AGE = ("ALL", "전체관람가")
    OVER_12 = ("12", "12세이상관람가")
    OVER_15 = ("15", "15세이상관람가")
    OVER_18 = ("18", "청소년관람불가")
    RESTRICTED = ("R18", "제한상영가")
    FILM_RATING_CHOICES = [ALL_AGE, OVER_12, OVER_15, OVER_18, RESTRICTED]
    film_rating = models.CharField(max_length=3, choices=FILM_RATING_CHOICES)

    synopsys = models.TextField(blank=True)

    directors = models.ManyToManyField("Director", related_name="filmography")
    writers = models.ManyToManyField("Writer", related_name="filmography")
    cast = models.ManyToManyField(
        "Actor", through="Character", related_name="filmography"
    )


class People(models.Model):
    name = models.CharField(max_length=50)
    biography = models.TextField(blank=True)

    def avatar_upload_to(self, filename):
        modelname = self.__class__.__name__.lower()
        return f"{modelname}s/{self.id}/avatar/{filename}"

    avatar = models.ImageField(blank=True, upload_to=avatar_upload_to)

    class Meta:
        abstract = True


class Director(People):
    pass


class Writer(People):
    pass


class Actor(People):
    pass


class Character(models.Model):
    name = models.CharField(max_length=50, blank=True)
    role = models.CharField()  # choices: Open API 스펙 보고 결정
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE)


class Country(models.Model):
    # follows ISO 3166-1
    alpha_2 = models.CharField(max_length=2, primary_key=True)
    name = models.CharField(max_length=50)


class Genre(models.Model):
    # from KMDb genre list
    name = models.CharField(max_length=7)


class Photo(models.Model):
    def image_upload_to(self, filename):
        modelname = self.__class__.__name__.lower()
        return f"movies/{self.movie_id}/{modelname}s/{filename}"

    image_url = models.ImageField(upload_to=image_upload_to)

    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)


class Video(models.Model):
    title = models.CharField(max_length=50)
    video_url = models.URLField(max_length=200)
    thumbnail_url = models.URLField(max_length=200)

    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
