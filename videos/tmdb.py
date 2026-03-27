import urllib.request
import urllib.parse
import json
from django.conf import settings

TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"


def _get(path: str, params: dict = {}) -> dict:
    params["api_key"] = settings.TMDB_API_KEY
    query = urllib.parse.urlencode(params)
    url = f"{TMDB_BASE}{path}?{query}"
    with urllib.request.urlopen(url, timeout=10) as res:
        return json.loads(res.read().decode())


def search_movies(query: str) -> list:
    data = _get("/search/movie", {"query": query, "language": "en-US", "page": 1})
    results = []
    for m in data.get("results", [])[:10]:
        results.append({
            "tmdb_id": m["id"],
            "title": m.get("title", ""),
            "overview": m.get("overview", ""),
            "release_date": m.get("release_date", ""),
            "poster_url": f"{TMDB_IMAGE_BASE}{m['poster_path']}" if m.get("poster_path") else None,
            "backdrop_url": f"https://image.tmdb.org/t/p/w1280{m['backdrop_path']}" if m.get("backdrop_path") else None,
            "vote_average": m.get("vote_average", 0),
            "genre_ids": m.get("genre_ids", []),
        })
    return results


def get_trailer_key(tmdb_id: int) -> str | None:
    data = _get(f"/movie/{tmdb_id}/videos", {"language": "en-US"})
    results = data.get("results", [])
    # prefer official YouTube trailer, fall back to any YouTube video
    for v in results:
        if v.get("site") == "YouTube" and v.get("type") == "Trailer" and v.get("official"):
            return v["key"]
    for v in results:
        if v.get("site") == "YouTube" and v.get("type") == "Trailer":
            return v["key"]
    for v in results:
        if v.get("site") == "YouTube":
            return v["key"]
    return None


def get_movie_metadata(tmdb_id: int) -> dict:
    m = _get(f"/movie/{tmdb_id}", {"language": "en-US", "append_to_response": "credits"})

    genres = [g["name"] for g in m.get("genres", [])]

    cast = m.get("credits", {}).get("cast", [])
    star_actors = ", ".join(
        [c["name"] for c in cast[:5]]
    )

    crew = m.get("credits", {}).get("crew", [])
    directors = [c["name"] for c in crew if c.get("job") == "Director"]
    producer_names = [c["name"] for c in crew if c.get("job") in ("Producer", "Executive Producer")]
    producer = ", ".join((directors or producer_names)[:2]) or "Unknown"

    return {
        "tmdb_id": m["id"],
        "title": m.get("title", ""),
        "description": m.get("overview", ""),
        "release_date": m.get("release_date", ""),
        "poster_url": f"{TMDB_IMAGE_BASE}{m['poster_path']}" if m.get("poster_path") else None,
        "backdrop_url": f"https://image.tmdb.org/t/p/w1280{m['backdrop_path']}" if m.get("backdrop_path") else None,
        "star_actors": star_actors,
        "producer": producer,
        "genres": genres,
        "runtime": m.get("runtime"),
        "vote_average": m.get("vote_average", 0),
        "youtube_trailer_key": get_trailer_key(tmdb_id),
    }
