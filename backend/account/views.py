from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.settings import api_settings as simplejwt_settings
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .permissions import IsSelfOrAdmin
from .serializers import UserRetrieveSerializer, SignUpSerializer


class SignUpView(CreateAPIView):
    serializer_class = SignUpSerializer
    permission_classes = [AllowAny]


class UserRetrieveView(RetrieveAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserRetrieveSerializer
    permission_classes = [IsSelfOrAdmin]


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
            secure=True,
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
