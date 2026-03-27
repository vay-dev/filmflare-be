import os
import sys
import django
import requests

# Add the parent directory to the Python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# 1️⃣ Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# 2️⃣ Now you can safely import Django models
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from videos.models import Video, Genre

TMDB_ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJkMWQ1NDFjY2Y1YmY4NzMwMDc1N2ZjODI2MDNjNDc3YSIsIm5iZiI6MTc1NTQ2OTYwNS4yMTgsInN1YiI6IjY4YTI1NzI1OGE4MzQxNDgzMTYxYzM5ZCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.eWtWmXpKCHub7y8R5JgJhDlngQQAr9yzz2LVgOhV00M"

# Different movie categories for variety
TMDB_URLS = [
    "https://api.themoviedb.org/3/movie/popular?language=en-US&page=1",
    "https://api.themoviedb.org/3/movie/top_rated?language=en-US&page=1",
    "https://api.themoviedb.org/3/movie/now_playing?language=en-US&page=1",
]

HEADERS = {
    "Authorization": f"Bearer {TMDB_ACCESS_TOKEN}",
    "Content-Type": "application/json;charset=utf-8"
}

TMDB_GENRE_MAP = {
    28: "Action",
    12: "Adventure",
    16: "Animation",
    35: "Comedy",
    80: "Crime",
    18: "Drama",
    10751: "Family",
    14: "Fantasy",
    27: "Horror",
    9648: "Mystery",
    878: "Sci-Fi",
    53: "Thriller",
}


def run():
    User = get_user_model()
    admin = User.objects.filter(is_superuser=True).first()

    if not admin:
        print("Error: No superuser found. Please create a superuser first.")
        return

    print("Fetching movies from TMDB...")
    total_movies_added = 0
    movies_to_fetch = 30
    seen_titles = set()  # Track titles to avoid duplicates

    for url in TMDB_URLS:
        if total_movies_added >= movies_to_fetch:
            break

        print(f"\nFetching from: {url.split('/')[-1].split('?')[0]}...")
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()

        for movie in data.get("results", []):
            if total_movies_added >= movies_to_fetch:
                break

            title = movie["title"]

            # Skip duplicates
            if title in seen_titles:
                continue

            # Check if movie already exists in database
            if Video.objects.filter(title=title).exists():
                print(f"Skipped (already exists): {title}")
                continue

            seen_titles.add(title)
            description = movie["overview"] or "No description"
            release_date = movie.get("release_date") or "2025-01-01"

            # Map TMDB genres
            genres = []
            for g_id in movie.get("genre_ids", []):
                genre_name = TMDB_GENRE_MAP.get(g_id, "Unknown")
                # Use filter().first() to avoid MultipleObjectsReturned error
                genre = Genre.objects.filter(name=genre_name.lower()).first()
                if not genre:
                    genre = Genre.objects.create(name=genre_name.lower())
                genres.append(genre)

            # Get poster path from TMDB
            poster_path = movie.get("poster_path")
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None

            # Create Video object
            video = Video.objects.create(
                title=title,
                description=description,
                release_date=release_date,
                producer="Unknown",
                star_actors="Unknown",
                uploaded_by=admin,
                video_file="/videos/default.mp4"
            )

            # Download and save poster if available
            if poster_url:
                try:
                    poster_response = requests.get(poster_url)
                    poster_response.raise_for_status()
                    video.thumbnail.save(
                        f"{title.replace(' ', '_').replace('/', '_')}_poster.jpg",
                        ContentFile(poster_response.content),
                        save=False
                    )
                    print(f"  ✓ Downloaded poster for: {title}")
                except Exception as e:
                    print(f"  ⚠️ Could not download poster for {title}: {e}")

            video.genres.set(genres)
            video.save()

            total_movies_added += 1
            print(f"Added ({total_movies_added}/{movies_to_fetch}): {title}")

    print(f"\nDone! Added {total_movies_added} movies from TMDB!")


if __name__ == "__main__":
    run()
