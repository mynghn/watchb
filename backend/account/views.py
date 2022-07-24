from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.settings import api_settings as simple_jwt_settings
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import SignUpSerializer


class SignUpView(CreateAPIView):
    serializer_class = SignUpSerializer
    permission_classes = [AllowAny]


class JWTObtainPairView(TokenObtainPairView):
    def post(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        # 1. access token in payload
        response = Response(
            {"access": serializer.validated_data["access"]}, status=HTTP_200_OK
        )
        # 2. refresh token in cookie
        response.set_cookie(
            key=simple_jwt_settings["REFRESH_TOKEN_COOKIE_KEY"],
            value=serializer.validated_data["refresh"],
            max_age=simple_jwt_settings["REFRESH_TOKEN_LIFETIME"].total_seconds(),
            secure=True,
            httponly=True,
        )

        return response
