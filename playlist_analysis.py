import requests
from spotify_api import get_artist_genres

class PlaylistAnalyzer:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://api.spotify.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

    def get_all_playlists(self):
        playlists = []
        url = f"{self.base_url}/me/playlists?limit=50"

        while url:
            response = requests.get(url, headers=self.headers)
            data = response.json()
            playlists.extend(data["items"])
            url = data["next"]

        return playlists

    def get_playlist_details(self, playlist_id):
        url = f"{self.base_url}/playlists/{playlist_id}"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_top_playlists(self, playlists, n=2):
        sorted_playlists = sorted(playlists, key=lambda x: x["tracks"]["total"], reverse=True)
        return sorted_playlists[:n]

    def extract_artist_ids_from_playlist(self, playlist):
        artist_ids = []
        tracks = playlist["tracks"]["items"]
        for item in tracks:
            track = item.get("track")
            if not track:
                continue
            for artist in track.get("artists", []):
                artist_id = artist.get("id")
                if artist_id:
                    artist_ids.append(artist_id)
        return artist_ids

    def analyze_genres_from_playlists(self, playlists):
        from collections import Counter
        genre_counts = Counter()
        playlist_summaries = []

        for playlist in playlists:
            details = self.get_playlist_details(playlist["id"])
            artist_ids = self.extract_artist_ids_from_playlist(details)

            for artist_id in artist_ids:
                genres = get_artist_genres(artist_id, self.access_token)
                genre_counts.update(genres)

            summary = {
                "name": details.get("name", "Bilinmeyen Playlist"),
                "image": details.get("images", [{}])[0].get("url", ""),
                "track_count": details.get("tracks", {}).get("total", 0)
            }
            playlist_summaries.append(summary)

        return genre_counts, playlist_summaries
