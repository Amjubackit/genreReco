import json
import os
import os.path as osp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from utils.general_utls import is_file_valid, purify_text, get_common_genre
from utils.lyrics_utils import fetch_lyrics, LyricsHandler, save_lyrics


with open(osp.join(osp.dirname(osp.abspath(__file__)), 'creds.json'), 'r') as fp:
    creds_dict = json.load(fp)

spotify = spotipy.Spotify(
    client_credentials_manager=SpotifyClientCredentials(**creds_dict)
)


def fetch_tracks(search_query=None, limit=10, offset=0):
    if search_query is None:
        search_query = ""
    print(f"SEARCH QUERY: {search_query}")
    response = spotify.search(search_query, limit=limit, offset=offset, type="track")
    return response.get("tracks", {}).get("items", [])


def fetch_track_data(track_obj):
    try:
        track_data = extract_tracks_data(track_obj, audio_features=False)
        purified_artists = purify_text(track_data.get('artists'))
        purified_name = purify_text(track_data.get('name'))
        genius_url = f"https://genius.com/{purified_artists}-{purified_name}-lyrics"
        lyrics_file = os.path.join("song_lyrics", f"{purified_artists}-{purified_name}.txt")
        track_data["lyrics_file"] = lyrics_file
        track_data["lyrics_url"] = genius_url
        if not is_file_valid(lyrics_file):
            print("LYRICS FILE IS NOT FOUND OR NOT VALID")
            lyrics = fetch_lyrics(genius_url)
            if not lyrics:
                print("RETURNS PARTIAL DATA DUE TO LYRICS FETCH FAILURE")
                return track_data

            save_lyrics(''.join(lyrics), lyrics_file)

        print(f"INIT HANDLER FOR FILE: {lyrics_file}")
        lyrics_handler = LyricsHandler(lyrics_file)
        lyrics_features = lyrics_handler.extract_lyrics_features()
        print(f"EXTRACTED FEATURES:\n{lyrics_features}")
        track_data.update(lyrics_features)

        return track_data

    except Exception as err:
        print(f"FAILED FETCH TRACK DATA: {err}")


def extract_tracks_data(track, audio_features=False):
    print(f"EXTRACTING TRACK FEATURES, AUDIO FEATURES = {audio_features}")
    artists = track.get("artists", [])[0]
    artist_id = artists.get("id")
    artist_info = spotify.artist(artist_id)
    artist_genres = artist_info.get("genres", [])
    release_date = track.get("album", {}).get("release_date")

    track_dict = {
        "name": str(track.get("name")),
        "artists": str(artist_info.get("name")),
        "release_year": int(release_date.split("-")[0]),
        "release_month": int(release_date.split("-")[1]) if "-" in release_date else None,
        "genres": list(artist_genres),
        "common_genre": get_common_genre(artist_genres),
        "duration": int(track.get("duration_ms")),
        "popularity": int(track.get("popularity"))
    }

    if audio_features:
        track_audio_features = spotify.audio_features(track.get("uri"))[0]
        track_dict.update(**{key: float(track_audio_features.get(key)) for key in
                             ["danceability", "energy", "key", "loudness", "speechiness", "acousticness",
                              "instrumentalness",
                              "liveness", "valence", "tempo"]})

    return track_dict


if __name__ == '__main__':
    test = spotify.artist("6zVFRTB0Y1whWyH7ZNmywf")
    print(test)
