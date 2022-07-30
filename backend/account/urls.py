from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("users", views.UserViewSet, basename="user")

urlpatterns = [
    *router.urls,
    path(
        "auth/token-pair/obtain/",
        views.JWTObtainPairView.as_view(),
        name="obtain-token-pair",
    ),
    path(
        "auth/token-pair/refresh/",
        views.JWTRefreshView.as_view(),
        name="refrsh-token-pair",
    ),
    path(
        "auth/refresh-token/expire/",
        views.RefreshTokenExpireView.as_view(),
        name="expire-refresh-token",
    ),
]
