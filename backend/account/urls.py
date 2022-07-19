from django.urls import path

from . import views

urlpatterns = [
    path("accounts/", views.SignUpView.as_view(), name="sign-up"),
]
