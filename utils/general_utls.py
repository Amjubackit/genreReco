import random
import re
from collections import Counter
import os
import pandas as pd

GENRE_LIST = [
    'pop', 'rock', 'hip-hop', 'rap', 'r&b', 'soul', 'electronic', 'dance', 'country', 'jazz', 'classical',
    'reggae', 'alternative', 'indie', 'folk', 'metal', 'punk', 'blues', 'world', 'funk', 'disco', 'gospel'
]


def fix_genre(genre_string):
    mapping = {
        'canadian hip hop': 'hip-hop',
        'lgbtq+ hip hop': 'hip-hop',
        'hip hop': 'hip-hop',
        'hip pop': 'hip-hop',
        "metalcore": "metal",
        "k-pop": "pop",
    }
    # Return genre mapped genre if matched
    if genre_string.lower() in mapping.keys():
        return mapping.get(genre_string)

    # If got here genre is not recognized, will not be counted
    return genre_string


def split_list_items(list_items):
    merged_list = [item.split() for item in list_items]
    flattened_list = [word for sublist in merged_list for word in sublist]
    return flattened_list


def remove_non_genres(word_list):
    # Search weired genre patterns for each genre in genre list
    # Returns actual genre list
    # Avoid counting trap as rap
    return [genre for genre in GENRE_LIST for item in word_list if genre in item and item != 'trap']


def get_common_genre(song_genres):
    dash_removed = [item.replace("-", " ") for item in song_genres]
    split_list = [item.partition("hip hop") for item in dash_removed]
    flatten = [subitem for item in split_list for subitem in item if subitem]
    fixed_list = [fix_genre(item) for item in flatten]
    new_list = split_list_items(fixed_list)
    clean_list = remove_non_genres(new_list)
    if not clean_list:
        return

    genre_counts = Counter(clean_list)  # dict
    elements = [element for element, freq in genre_counts.items()]
    freqs = [freq for element, freq in genre_counts.items()]
    # Choose randomly between the known genres!
    return random.choices(elements,freqs)[0]


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


def remove_file(file_path):
    try:
        os.remove(file_path)
        print("File removed successfully")
    except OSError as e:
        pass


def save_dataset(data, filepath, overwrite=False):
    # Convert raw data into pandas df for an easier save
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)

    if overwrite or not os.path.exists(filepath):
        # write mode by default, overwrites csv data
        data.to_csv(filepath, index=False)

    else:
        # Append to an existing csv file, ignore header
        data.to_csv(filepath, index=False, mode="a", header=False)

    print(f"Data successfully saved as '{filepath}'.")


def load_dataset(filepath):
    return pd.read_csv(filepath)


def is_file_valid(file_path):
    if os.path.exists(file_path):
        file_size = os.stat(file_path).st_size
        return file_size > 0
    return False
