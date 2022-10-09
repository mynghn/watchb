from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import (
    Blocklist,
    Movie,
    Person,
    PersonLike,
    Rating,
    Review,
    ReviewLike,
    Wishlist,
)

admin.site.register(Movie, ModelAdmin)
admin.site.register(Person, ModelAdmin)
admin.site.register(Rating, ModelAdmin)
admin.site.register(Review, ModelAdmin)
admin.site.register(Wishlist, ModelAdmin)
admin.site.register(Blocklist, ModelAdmin)
admin.site.register(ReviewLike, ModelAdmin)
admin.site.register(PersonLike, ModelAdmin)
