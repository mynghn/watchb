from accounts.permissions import IsAuthorOrAdmin
from rest_framework.generics import RetrieveAPIView
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, UpdateModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import GenericViewSet

from movies.models import Blocklist, Movie, Rating, Review, Wishlist
from serializers import IndexedListSerializer
from views import CollectUserFromRequestMixin

from .serializers import (
    BlocklistCreateSerializer,
    MovieRetrieveSerializer,
    RatingCreateSerializer,
    RatingListSerializer,
    RatingUpdateSerializer,
    ReviewCreateSerializer,
    ReviewListSerializer,
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
    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]
        elif self.action in ("update", "partial_update", "destroy"):
            return [IsAuthorOrAdmin()]
        elif self.action == "list":
            return [AllowAny()]
        else:
            return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            return RatingCreateSerializer
        elif self.action in ("update", "partial_update"):
            return RatingUpdateSerializer
        elif self.action == "list":
            return RatingListSerializer
        else:
            return Serializer

    def get_queryset(self):
        if self.action == "list":
            query_params_data = self.request.query_params.dict()
            query_params_data.pop("index_key", None)
            rating_search_serializer = self.get_serializer(data=query_params_data)
            rating_search_serializer.is_valid(raise_exception=True)
            return Rating.objects.filter(**rating_search_serializer.validated_data)
        else:
            return Rating.objects.all()

    # TODO: pagination
    def list(self, request: Request, *args, **kwargs) -> Response:
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer: IndexedListSerializer = self.get_serializer(
            queryset,
            many=True,
            index_key=self.request.query_params.get("index_key"),
        )
        return Response(serializer.data)


class ReviewViewSet(
    CollectUserFromRequestMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]
        elif self.action in ("update", "partial_update", "destroy"):
            return [IsAuthorOrAdmin()]
        elif self.action == "list":
            return [AllowAny()]
        else:
            return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            return ReviewCreateSerializer
        elif self.action in ("update", "partial_update"):
            return ReviewUpdateSerializer
        elif self.action == "list":
            return ReviewListSerializer
        else:
            return Serializer

    def get_queryset(self):
        if self.action == "list":
            query_params_data = self.request.query_params.dict()
            query_params_data.pop("index_key", None)
            review_search_serializer = self.get_serializer(data=query_params_data)
            review_search_serializer.is_valid(raise_exception=True)
            return Review.objects.filter(**review_search_serializer.validated_data)
        else:
            return Review.objects.all()

    # TODO: pagination
    def list(self, request: Request, *args, **kwargs) -> Response:
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer: IndexedListSerializer = self.get_serializer(
            queryset,
            many=True,
            index_key=self.request.query_params.get("index_key"),
        )
        return Response(serializer.data)


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
