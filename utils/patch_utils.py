import ast
from utils.general_utls import get_common_genre, is_file_valid
from utils.lyrics_utils import LyricsHandler


def recalculate_dataset(dataset_df):
    for i, row in dataset_df.iterrows():
        genre_list = row["genres"]
        # Convert genres back to list
        genre_list = ast.literal_eval(genre_list)
        recalculate_common_genre = get_common_genre(genre_list)
        if recalculate_common_genre != row['common_genre']:
            print(f"common_genre CHANGED FROM {row['common_genre']} TO {recalculate_common_genre}")
            dataset_df.at[i, 'common_genre'] = recalculate_common_genre

        lyrics_file = row["lyrics_file"]
        if not is_file_valid(lyrics_file):
            print("LYRICS FILE IS NOT FOUND OR NOT VALID")
            continue

        print(f"INIT HANDLER FOR FILE: {lyrics_file}")
        lyrics_handler = LyricsHandler(lyrics_file)
        lyrics_features = lyrics_handler.extract_lyrics_features()
        for feature in lyrics_features:
            dataset_df.at[i, feature] = lyrics_features[feature]

    print("DONE")
