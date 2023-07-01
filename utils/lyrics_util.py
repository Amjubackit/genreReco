import json
import os
import re
import pandas as pd
import requests
from bs4 import BeautifulSoup
from nltk.corpus import words
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from utils.general_utls import is_file_valid, purify_text

WORD_LIST = set(words.words())
STOPWORD_LIST = set(stopwords.words('english'))


class LyricsHandler:
    def __init__(self, lyrics_file):
        if not is_file_valid(lyrics_file):
            raise FileNotFoundError

        self.lyrics_raw = self.load_song_lyrics(lyrics_file)
        self.lyrics_lines = [line for line in self.lyrics_raw.split("\n") if line]
        self.clean_lyrics = self.clean_lyrics_string(" ".join(self.lyrics_lines))
        self.tokenized_lyrics = word_tokenize(self.clean_lyrics)

    @staticmethod
    def load_song_lyrics(text_file):
        with open(text_file, 'r') as tf:
            string = tf.read()
        return string.lower()

    @staticmethod
    def clean_lyrics_string(string):
        string = re.sub(r'-', ' ', string)
        # Allow only letters, but remove anything inside a [] before to get rid of vers/chorus/singer names
        return re.sub(r'[^a-zA-Z\s]', '', re.sub(r'\[.*?\]', '', string))

    @staticmethod
    def is_slang_word(word):
        # Check if the word has a sense in WordNet with a part-of-speech tag indicating it is slang
        synsets = wordnet.synsets(word)
        print(synsets)
        return any('.s' in synset.name() for synset in synsets)

    @staticmethod
    def is_stop_word(word):
        return word.lower() in STOPWORD_LIST

    def vers_chorus_count(self):
        vers_count = 0
        chorus_count = 0
        for line in self.lyrics_lines:
            first_word = line.split(" ")[0]
            if first_word.startswith("[chorus"):
                chorus_count += 1
            elif first_word.startswith("[verse"):
                vers_count += 1
        return vers_count, chorus_count

    def count_words_by_type(self, word_type, unique=False):
        if word_type == "slang":
            return self.count_special_words(self.is_slang_word, unique)
        if word_type == "stop":
            return self.count_special_words(self.is_stop_word, unique)
        if word_type == "all":
            return len(self.clean_lyrics.split(" ")) if not unique else len(set(self.clean_lyrics.split(" ")))

    def count_special_words(self, detect_func, unique):
        word_list = self.tokenized_lyrics if not unique else set(self.tokenized_lyrics)
        return [word for word in word_list if detect_func(word)]
        # return sum(1 for word in word_list if detect_func(word))

    def sentiment_analysis(self):
        sid = SentimentIntensityAnalyzer()
        sentiment = sid.polarity_scores(self.clean_lyrics)
        return sentiment

    def extract_lyrics_features(self):
        word_count = self.count_words_by_type("all")
        unique_words = self.count_words_by_type("all", unique=True)
        stopword_count = self.count_words_by_type("stop")
        slang_word_count = self.count_words_by_type("slang")
        vers_cnt, chorus_cnt = self.vers_chorus_count()
        sentiment = self.sentiment_analysis()

        features = {
            "lines_count": len(self.lyrics_lines),
            "word_count": word_count,
            "unique_words": unique_words,
            "stopword_count": stopword_count,
            "slang_word_count": slang_word_count,
            "chorus_count": chorus_cnt,
            "verse_count": vers_cnt,
            **sentiment
        }
        return features


def fetch_lyrics(artist, song_title):
    # Format the artist and song title for the URL
    print(f"\nARTIST: {artist}")
    print(f"SONG TITLE: {song_title}")
    artist = purify_text(artist)
    song_title = purify_text(song_title)
    url = f"https://genius.com/{artist}-{song_title}-lyrics"

    print(f"Fetching: {url}")
    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        print("I got something")
        # Use BeautifulSoup to parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the lyrics section
        lyrics_divs = soup.find_all('div', attrs={"data-lyrics-container": "true"})

        lyrics_lines = [d.get_text('\n') for d in lyrics_divs]

        return lyrics_lines

    print(f"Lyrics data not found")
    # Return None if lyrics couldn't be fetched
    return None


if __name__ == '__main__':
    filepath = "/Users/bar-study/PycharmProjects/genreReco/song_lyrics/system-of-a-down-chop-suey.txt"
    lyrics_handler = LyricsHandler(filepath)

    # print(lyrics_handler.lyrics_string)
    # print(lyrics_handler.lyrics_lines)

    # wc = lyrics_handler.vers_chorus_count()
    # print(wc)

    # sw = lyrics_handler.clean_lyrics
    # print(sw)

    # slangs = lyrics_handler.count_words_by_type("slang")
    # print(slangs)
    # print(json.dumps(sw, indent=2))
    # is_slang = lyrics_handler.is_stop_word("it's")
    # print(is_slang)
    #
    is_slang = lyrics_handler.is_slang_word("gonna")
    print(is_slang)
