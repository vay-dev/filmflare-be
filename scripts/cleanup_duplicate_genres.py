import os
import sys
import django

# Add the parent directory to the Python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Now import Django models
from videos.models import Genre, Video
from django.db.models import Count

def cleanup_duplicate_genres():
    """Remove duplicate genres and keep only one of each."""
    print("Checking for duplicate genres...")

    # Find all genre names that have duplicates
    duplicates = Genre.objects.values('name').annotate(
        count=Count('id')
    ).filter(count__gt=1)

    if not duplicates:
        print("No duplicate genres found!")
        return

    print(f"Found {len(duplicates)} duplicate genre names:")
    for dup in duplicates:
        print(f"  - {dup['name']} ({dup['count']} copies)")

    # For each duplicate genre name, keep the first one and delete the rest
    for dup in duplicates:
        genre_name = dup['name']
        genres = Genre.objects.filter(name=genre_name).order_by('id')

        # Keep the first one
        primary_genre = genres.first()
        duplicate_genres = genres[1:]

        print(f"\nProcessing '{genre_name}':")
        print(f"  Keeping Genre ID {primary_genre.id}")

        # Update all videos that use duplicate genres to use the primary one
        for duplicate in duplicate_genres:
            print(f"  Removing duplicate Genre ID {duplicate.id}")

            # Find all videos using this duplicate genre
            videos_with_duplicate = Video.objects.filter(genres=duplicate)
            for video in videos_with_duplicate:
                # Add the primary genre if not already there
                if not video.genres.filter(id=primary_genre.id).exists():
                    video.genres.add(primary_genre)
                # Remove the duplicate genre
                video.genres.remove(duplicate)

            # Delete the duplicate genre
            duplicate.delete()

    print("\nCleanup complete!")

    # Show final genre list
    all_genres = Genre.objects.all().order_by('name')
    print(f"\nFinal genre list ({all_genres.count()} total):")
    for genre in all_genres:
        print(f"  - {genre.name} (ID: {genre.id})")

if __name__ == "__main__":
    cleanup_duplicate_genres()
