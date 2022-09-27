from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.settings import api_settings as simplejwt_settings
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .permissions import IsSelfOrAdmin
from .serializers import (
    SignUpSerializer,
    UserDetailSerializer,
    UserListSerializer,
    UserUpdateSerializer,
)

User = get_user_model()


class UserViewSet(
    UpdateModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    ListModelMixin,
    GenericViewSet,
):
    def get_serializer_class(self):
        if self.action == "create" or (self.action == "metadata" and not self.detail):
            return SignUpSerializer
        elif self.action in ("update", "partial_update"):
            return UserUpdateSerializer
        elif self.action == "retrieve":
            return UserDetailSerializer
        elif self.action == "list":
            return UserListSerializer
        else:
            return Serializer

    def get_permissions(self):
        if self.action in ("create", "list"):
            return [AllowAny()]
        elif self.action in ("retrieve", "update", "partial_update"):
            return [IsSelfOrAdmin()]
        else:
            return super().get_permissions()

    def get_queryset(self):
        if self.action == "list":
            user_search_serializer = self.get_serializer(
                data=self.request.query_params.dict()
            )
            user_search_serializer.is_valid(raise_exception=True)
            return User.objects.filter(**user_search_serializer.validated_data)
        else:
            return User.objects.all()


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
