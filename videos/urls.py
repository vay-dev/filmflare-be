from django.urls import path
from .views import GenreViewSet, VideoViewset, tmdb_search, tmdb_metadata, tmdb_poster_proxy
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'videos', VideoViewset, basename='videos')
router.register(r'genres', GenreViewSet, basename='genres')

urlpatterns = router.urls + [
    path('tmdb/search/', tmdb_search),
    path('tmdb/metadata/', tmdb_metadata),
    path('tmdb/poster/', tmdb_poster_proxy),
]
