from django.urls import path
from rest_framework_simplejwt.views import token_refresh

from . import views

urlpatterns = [
    path("", views.SignUpView.as_view(), name="sign-up"),
    path("jwt/", views.JWTObtainPairView.as_view(), name="token-obtain-pair"),
    path("jwt/refresh/", token_refresh, name="token-refresh"),
]
