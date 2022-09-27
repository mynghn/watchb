from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import Movie, People

admin.site.register(Movie, ModelAdmin)
admin.site.register(People, ModelAdmin)
