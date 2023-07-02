import ast
from utils.general_utls import get_common_genre


def recalculate_dataset(dataset_df):
    # Remove avg word length
    dataset_df.drop(columns=['avg_word_length'], axis=1, inplace=True)

    for i, row in dataset_df.iterrows():
        genre_list = row["genres"]
        # Convert genres back to list
        genre_list = ast.literal_eval(genre_list)
        recalculate_common_genre = get_common_genre(genre_list)
        if recalculate_common_genre != row['common_genre']:
            print(f"common_genre CHANGED FROM {row['common_genre']} TO {recalculate_common_genre}")
            dataset_df.at[i,'common_genre'] = recalculate_common_genre

    print("DONE")