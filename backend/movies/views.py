from accounts.permissions import IsAuthorOrAdmin
from rest_framework.generics import RetrieveAPIView
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, UpdateModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.serializers import Serializer
from rest_framework.viewsets import GenericViewSet

from mixins.view import CollectUserFromRequestMixin
from movies.models import Blocklist, Movie, Rating, Review, Wishlist

from .serializers import (
    BlocklistCreateSerializer,
    MovieRetrieveSerializer,
    RatingCreateSerializer,
    RatingUpdateSerializer,
    ReviewCreateSerializer,
    ReviewUpdateSerializer,
    WishlistCreateSerializer,
)


class MovieRetrieveView(RetrieveAPIView):
    serializer_class = MovieRetrieveSerializer
    permission_classes = [AllowAny]
    queryset = Movie.objects.all()


class RatingViewSet(
    CollectUserFromRequestMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    queryset = Rating.objects.all()

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]
        elif self.action in ("update", "partial_update", "destroy"):
            return [IsAuthorOrAdmin()]
        else:
            return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            return RatingCreateSerializer
        elif self.action in ("update", "partial_update"):
            return RatingUpdateSerializer
        else:
            return Serializer


class ReviewViewSet(
    CollectUserFromRequestMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    queryset = Review.objects.all()

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]
        elif self.action in ("update", "partial_update", "destroy"):
            return [IsAuthorOrAdmin()]
        else:
            return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            return ReviewCreateSerializer
        elif self.action in ("update", "partial_update"):
            return ReviewUpdateSerializer
        else:
            return Serializer


class WishlistViewSet(
    CollectUserFromRequestMixin, CreateModelMixin, DestroyModelMixin, GenericViewSet
):
    serializer_class = WishlistCreateSerializer
    queryset = Wishlist.objects.all()

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]
        elif self.action == "destroy":
            return [IsAuthorOrAdmin()]
        else:
            return super().get_permissions()


class BlocklistViewSet(
    CollectUserFromRequestMixin, CreateModelMixin, DestroyModelMixin, GenericViewSet
):
    serializer_class = BlocklistCreateSerializer
    queryset = Blocklist.objects.all()

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]
        elif self.action == "destroy":
            return [IsAuthorOrAdmin()]
        else:
            return super().get_permissions()
