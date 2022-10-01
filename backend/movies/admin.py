from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import Movie, Person

admin.site.register(Movie, ModelAdmin)
admin.site.register(Person, ModelAdmin)
