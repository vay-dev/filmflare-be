from django.db import models
from django.conf import settings

# Create your models here.


class Video(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=300, blank=True, null=True)
    release_date = models.DateField()
    producer = models.CharField(max_length=255)
    star_actors = models.CharField(max_length=255)
    thumbnail = models.ImageField(upload_to='thumbnails/')
    video_file = models.FileField(upload_to='videos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    genres = models.ManyToManyField('Genre', related_name='videos', blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_videos'
    )

    youtube_trailer_key = models.CharField(max_length=20, blank=True, null=True)

    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_videos',
        blank=True,
    )

    def average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return sum(r.rating for r in ratings) / ratings.count()
        return 0

    def __str__(self):
        return self.title


class Rating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    video = models.ForeignKey(
        Video, on_delete=models.CASCADE, related_name='ratings')
    rating = models.PositiveIntegerField()

    class Meta:
        unique_together = ('user', 'video')

    def __str__(self):
        return f'{self.user.username} rated {self.video.title} ({self.rating})'


class Genre(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
