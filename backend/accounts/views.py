from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.settings import api_settings as simplejwt_settings
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from views import SearchAndListModelMixin

from .permissions import IsSelfOrAdmin
from .serializers import (
    SignUpSerializer,
    UserAvatarUpdateSerializer,
    UserBackgroundUpdateSerializer,
    UserFollowingsPartialUpdateSerializer,
    UserFollowingsRetrieveAndUpdateSerializer,
    UserListSerializer,
    UserRetrieveSerializer,
    UserUpdateSerializer,
)

User = get_user_model()


class UserViewSet(
    SearchAndListModelMixin,
    UpdateModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    GenericViewSet,
):
    queryset = User.objects.all()
    qstring_serializer_class = UserListSerializer

    def get_serializer_class(self):
        if self.action == "create" or (self.action == "metadata" and not self.detail):
            return SignUpSerializer
        elif self.action in ("update", "partial_update"):
            return UserUpdateSerializer
        elif self.action == "retrieve":
            return UserRetrieveSerializer
        elif self.action == "avatar":
            return UserAvatarUpdateSerializer
        elif self.action == "background":
            return UserBackgroundUpdateSerializer
        elif self.action == "followings":
            if self.request.method in ("GET", "PUT"):
                return UserFollowingsRetrieveAndUpdateSerializer
            elif self.request.method == "PATCH":
                return UserFollowingsPartialUpdateSerializer
        else:
            return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ("create", "list"):
            return [AllowAny()]
        elif self.action in (
            "retrieve",
            "update",
            "partial_update",
            "avatar",
            "background",
        ):
            return [IsSelfOrAdmin()]
        elif self.action == "followings":
            if self.request.method == "GET":
                return [IsAuthenticated()]
            elif self.request.method in ("PUT", "PATCH"):
                return [IsSelfOrAdmin()]
        else:
            return super().get_permissions()

    @action(detail=True, methods=["POST", "DELETE"])
    def avatar(self, request: Request, *args, **kwargs) -> Response:
        if self.request.method == "POST":
            return self.update(request, *args, **kwargs)
        elif self.request.method == "DELETE":
            self.get_object().avatar.delete()
            return Response(status=HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["POST", "DELETE"])
    def background(self, request: Request, *args, **kwargs) -> Response:
        if self.request.method == "POST":
            return self.update(request, *args, **kwargs)
        elif self.request.method == "DELETE":
            self.get_object().background.delete()
            return Response(status=HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["GET", "PUT", "PATCH"])
    def followings(self, request: Request, *args, **kwargs) -> Response:
        if self.request.method == "GET":
            return self.retrieve(request, *args, **kwargs)
        elif self.request.method in ("PUT", "PATCH"):
            return self.update(request, *args, **kwargs)


class JWTResponseMixin:
    def post(self, request: Request, *args, **kwargs) -> Response:
        # 1. leave only access token in payload
        response = super().post(request, *args, **kwargs)
        refresh_token = response.data.pop("refresh")
        # 2. set refresh token in cookie
        response.set_cookie(
            key=settings.JWT_REFRESH_TOKEN_COOKIE_KEY,
            value=refresh_token,
            max_age=simplejwt_settings.REFRESH_TOKEN_LIFETIME.total_seconds(),
            secure=not settings.DEBUG,
            httponly=True,
        )

        return response


class JWTObtainPairView(JWTResponseMixin, TokenObtainPairView):
    pass


class JWTRefreshView(JWTResponseMixin, TokenRefreshView):
    def post(self, request: Request, *args, **kwargs) -> Response:
        request.data.update(
            {"refresh": request.COOKIES.get(settings.JWT_REFRESH_TOKEN_COOKIE_KEY)}
        )
        return super().post(request, *args, **kwargs)


class RefreshTokenExpireView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        response = Response(status=HTTP_200_OK)
        response.set_cookie(
            key=settings.JWT_REFRESH_TOKEN_COOKIE_KEY,
            value="",
            expires="Mon, 1 Jan 1900 00:00:00 GMT",
        )
        return response
