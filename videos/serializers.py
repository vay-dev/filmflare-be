from rest_framework import serializers
from .models import Rating, Genre, Video


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']


class RatingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Rating
        fields = ['id', 'user', 'rating']
        read_only_fields = ['user']


class VideoSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.StringRelatedField(read_only=True)
    genres = GenreSerializer(many=True, read_only=True)
    likes_count = serializers.IntegerField(
        source='likes.count', read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    has_liked = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = [
            'id', 'title', 'description', 'release_date', 'producer',
            'star_actors', 'thumbnail', 'video_file', 'youtube_trailer_key',
            'uploaded_by', 'genres', 'likes_count', 'average_rating',
            'created_at', 'has_liked',
        ]
        read_only_fields = ['uploaded_by']
        extra_kwargs = {
            'video_file': {'required': False, 'allow_null': True},
        }

    def get_has_liked(self, obj):
        request = self.context.get('request')
        user = request.user if request else None
        if user and user.is_authenticated:
            return obj.likes.filter(id=user.id).exists()
        return False
