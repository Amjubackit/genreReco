import re
from collections import Counter
import csv
import os
import pandas as pd

GENRE_LIST = [
    'pop', 'rock', 'hip-hop', 'rap', 'r&b', 'soul', 'electronic', 'dance', 'country', 'jazz', 'classical',
    'reggae', 'alternative', 'indie', 'folk', 'metal', 'punk', 'blues', 'world', 'funk', 'disco', 'gospel'
]


def fix_genre(genre_string):
    mapping = {'hip hop': 'hip-hop', 'hip pop': 'hip-hop', "metalcore": "metal"}
    if genre_string.lower() not in mapping.keys():
        return genre_string

    return mapping.get(genre_string)


def split_list_items(list_items):
    merged_list = [item.split() for item in list_items]
    flattened_list = [fix_genre(word) for sublist in merged_list for word in sublist]
    return flattened_list


def remove_non_genres(word_list):
    return [item for item in word_list if item in GENRE_LIST]


def get_common_genre(song_genres):
    translated = [fix_genre(item) for item in song_genres]
    new_list = split_list_items(translated)
    clean_list = remove_non_genres(new_list)
    genre_counts = Counter(clean_list)
    most_common_genre = genre_counts.most_common(1)
    return most_common_genre[0][0]


def purify_text(text):
    # Make replace table
    trans_table = str.maketrans({'&': 'and', 'é': 'e'})
    text = text.translate(trans_table)
    # Remove anything inside parentheses (including parentheses)
    text = re.sub(r'\([^)]*\)', '', text)
    # Remove special characters
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    # Remove extra spaces
    text = ' '.join(text.split())
    # Replace spaces with dash
    text = re.sub(r'\s', '-', text)

    return text.lower()


def save_lyrics(txt, file_path):
    with open(file_path, 'w') as file:
        file.write(txt)


def remove_file(file_path):
    try:
        os.remove(file_path)
        print("File removed successfully")
    except OSError as e:
        pass


def save_dataset(data, filepath, overwrite=False):
    # Check if the file already exists and overwrite is not enabled
    if os.path.exists(filepath) and not overwrite:
        raise FileExistsError("File already exists. Set 'overwrite' to True to overwrite the file.")

    # Convert raw data into pandas df for an easier save
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)

    data.to_csv(filepath, index=False)
    print(f"Data successfully saved as '{filepath}'.")


def load_dataset(filepath):
    return pd.read_csv(filepath)


def is_file_valid(file_path):
    if os.path.exists(file_path):
        file_size = os.stat(file_path).st_size
        return file_size > 0
    return False


