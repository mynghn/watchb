from django.urls import path

from . import views

urlpatterns = [
    path("users/", views.SignUpView.as_view(), name="sign-up"),
    path("users/<int:pk>/", views.UserRetrieveView.as_view(), name="user-detail"),
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
