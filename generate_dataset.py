import os.path as osp
from utils.spotify_utils import fetch_tracks, fetch_track_data
from utils.general_utls import GENRE_LIST, save_dataset


if __name__ == '__main__':
    query = "year:1990-2023"
    file_name = "big_dataset_test.csv"
    song_per_genre = 2
    offset_range = int(song_per_genre/50) or 1
    print(f"GOING TO FETCH {song_per_genre*len(GENRE_LIST)} TRACKS")
    dataset_file_path = osp.join(osp.dirname(osp.abspath(__file__)), file_name)
    for genre in GENRE_LIST:
        for offset in range(offset_range):
            dataset = []
            limit = min(50, song_per_genre-50*offset)
            try:
                print(f"\nFETCHING {song_per_genre} {genre.upper()} SONGS, LIMIT: {limit}")
                res = fetch_tracks(query + f" genre:{genre}", limit=limit, offset=offset*50)
                if not res:
                    print(f"FAILED TO FETCH {genre.upper()} SONGS")
                    continue

                for index, track in enumerate(res):
                    print(f"\nPARSING SONG DATA ({index+1})")
                    data = {"source_genre": genre}
                    track_data = fetch_track_data(track)
                    data.update(track_data)
                    dataset.append(data)
                    print(f"SONG DATA SAVED")

                save_dataset(dataset, dataset_file_path, False)

            except Exception as e:
                print(f"FAILED FETCHING TRACKS: {e}")