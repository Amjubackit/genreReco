import json

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

SPOTIPY_CLIENT_ID = ""
SPOTIPY_CLIENT_SECRET = ""
spotify = spotipy.Spotify(
    client_credentials_manager=SpotifyClientCredentials(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET
    )
)


def fetch_random_tracks(search_query=None, limit=10):
    if search_query is None:
        search_query = {}
    response = spotify.search(search_query, type="track", limit=limit)
    return response.get("tracks", {}).get("items")


def extract_tracks_data(track):
    track_uri = track.get("uri")
    track_audio_features = spotify.audio_features(track_uri)[0]
    track_dict = {
        "artists": track.get("artists")[0].get("name"),
        "release_date": track.get("album", {}).get("release_date"),
        **{key: track.get(key) for key in
           ["name", "popularity", "uri", "duration_ms"]},
        **{key: track_audio_features.get(key) for key in
           ["danceability", "energy", "key", "loudness", "speechiness", "acousticness", "instrumentalness",
            "liveness", "valence", "tempo"]}
    }
    return track_dict


if __name__ == '__main__':
    query = {"year": "1900-2023"}
    res = fetch_random_tracks(query, 20)
    for track in res:
        data = extract_tracks_data(track)
        print(data)
