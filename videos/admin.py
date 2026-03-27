from django.contrib import admin
from .models import Video, Rating, Genre
# Register your models here.


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    ...


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    ...


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    ...
