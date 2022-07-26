from django.urls import path

from . import views

urlpatterns = [
    path("", views.SignUpView.as_view(), name="sign-up"),
    path("<int:pk>/", views.UserRetrieveView.as_view(), name="sign-up"),
    path("jwt/", views.JWTObtainPairView.as_view(), name="token-obtain-pair"),
    path("jwt/refresh/", views.JWTRefreshView.as_view(), name="token-refresh"),
]
