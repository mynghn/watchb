from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from .serializers import SignUpSerializer


class SignUpView(CreateAPIView):
    serializer_class = SignUpSerializer
    permission_classes = [AllowAny]
