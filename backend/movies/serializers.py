from rest_framework.serializers import ModelSerializer

from .models import (
    Blocklist,
    Country,
    Credit,
    Genre,
    Movie,
    Person,
    Poster,
    Rating,
    Review,
    Still,
    Video,
    Wishlist,
)


class CountryRetrieveSerializer(ModelSerializer):
    class Meta:
        model = Country
        fields = ["alpha_2", "name"]
        read_only_fields = fields


class GenreRetrieveSerializer(ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name"]
        read_only_fields = fields


class PersonRetrieveSerializer(ModelSerializer):
    class Meta:
        model = Person
        fields = ["id", "name", "avatar_url", "biography"]
        read_only_fields = fields


class CreditRetrieveSerializer(ModelSerializer):
    class Meta:
        model = Credit
        fields = ["id", "job", "cameo_type", "role_name", "person"]
        read_only_fields = fields

    person = PersonRetrieveSerializer()


class PosterRetrieveSerializer(ModelSerializer):
    class Meta:
        model = Poster
        fields = ["id", "image_url", "is_main"]
        read_only_fields = fields


class StillRetrieveSerializer(ModelSerializer):
    class Meta:
        model = Still
        fields = ["id", "image_url"]
        read_only_fields = fields


class VideoRetrieveSerializer(ModelSerializer):
    class Meta:
        model = Video
        fields = ["id", "title", "site", "external_id"]
        read_only_fields = fields


class MovieRetrieveSerializer(ModelSerializer):
    class Meta:
        model = Movie
        fields = [
            "id",
            "title",
            "release_date",
            "production_year",
            "running_time",
            "synopsys",
            "film_rating",
            "countries",
            "genres",
            "credits",
            "poster_set",
            "still_set",
            "video_set",
        ]
        read_only_fields = fields

    countries = CountryRetrieveSerializer(many=True)
    genres = GenreRetrieveSerializer(many=True)
    credits = CreditRetrieveSerializer(many=True)
    poster_set = PosterRetrieveSerializer(many=True)
    still_set = StillRetrieveSerializer(many=True)
    video_set = VideoRetrieveSerializer(many=True)


class RatingCreateSerializer(ModelSerializer):
    class Meta:
        model = Rating
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class RatingUpdateSerializer(ModelSerializer):
    class Meta(RatingCreateSerializer.Meta):
        read_only_fields = [
            "user",
            "movie",
        ] + RatingCreateSerializer.Meta.read_only_fields


class ReviewCreateSerializer(ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class ReviewUpdateSerializer(ModelSerializer):
    class Meta(ReviewCreateSerializer.Meta):
        read_only_fields = [
            "user",
            "movie",
        ] + ReviewCreateSerializer.Meta.read_only_fields


class WishlistCreateSerializer(ModelSerializer):
    class Meta:
        model = Wishlist
        fields = "__all__"
        read_only_fields = ["timestamp"]


class BlocklistCreateSerializer(ModelSerializer):
    class Meta:
        model = Blocklist
        fields = "__all__"
        read_only_fields = ["timestamp"]
