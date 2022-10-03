from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("ratings", views.RatingViewSet, basename="rating")
router.register("reviews", views.ReviewViewSet, basename="review")
router.register("wishlists", views.RatingViewSet, basename="wishlist")
router.register("blocklists", views.RatingViewSet, basename="blocklist")

urlpatterns = [
    *router.urls,
    path("movies/<int:pk>/", views.MovieRetrieveView.as_view(), name="movie-detail"),
]
