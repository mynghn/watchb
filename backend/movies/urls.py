from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("ratings", views.RatingViewSet, basename="ratings")
router.register("reviews", views.ReviewViewSet, basename="reviews")
router.register("wishlists", views.RatingViewSet, basename="wishlists")
router.register("blocklists", views.RatingViewSet, basename="blocklists")

urlpatterns = [
    *router.urls,
    path("movies/<int:pk>/", views.MovieRetrieveView.as_view(), name="movie-detail"),
]
