import json
import os
import re

import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)

# nltk.download('stopwords')
# nltk.download('punkt')
# nltk.download('cmudict')
# nltk.download('vader_lexicon')

from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.corpus import words

WORD_LIST = set(words.words())
STOPWORD_LIST = set(stopwords.words('english'))


class LyricsHandler:
    def __init__(self, lyrics_file):
        if not self.is_file_valid(lyrics_file):
            raise FileNotFoundError

        self.lyrics_string = self.load_song_lyrics(lyrics_file)
        self.lyrics_lines = [line for line in self.lyrics_string.split("\n") if line]
        self.clean_lyrics = re.sub(r'[^a-zA-Z\s]', '', self.lyrics_string)
        self.tokenized_lyrics = word_tokenize(self.clean_lyrics)

    @staticmethod
    def load_song_lyrics(text_file):
        with open(text_file, 'r') as tf:
            lyrics = re.sub(r'[^a-zA-Z0-9\s]', '', tf.read())
            # Remove extra spaces
            string = re.sub(r' +', ' ', lyrics)

        return string.lower()

    @staticmethod
    def is_file_valid(file_path):
        if os.path.exists(file_path):
            file_size = os.stat(file_path).st_size
            return file_size > 0
        return False

    @staticmethod
    def is_slang_word(word):
        return word.lower() not in WORD_LIST

    @staticmethod
    def is_stop_word(word):
        return word.lower() in STOPWORD_LIST

    def vers_chorus_count(self):
        vers_count = 0
        chorus_count = 0
        for line in self.lyrics_lines:
            first_word = line.split(" ")[0]
            if first_word == "chorus":
                chorus_count += 1
            elif first_word == "verse":
                vers_count += 1
        return vers_count, chorus_count

    def count_words_by_type(self, word_type, unique=False):
        if word_type == "slang":
            return self.count_special_words(self.is_slang_word, unique)
        if word_type == "stop":
            return self.count_special_words(self.is_stop_word, unique)
        if word_type == "all":
            return len(self.lyrics_string.split(" ")) if not unique else len(set(self.lyrics_string.split(" ")))

    def count_special_words(self, detect_func, unique):
        word_list = self.tokenized_lyrics if not unique else set(self.tokenized_lyrics)
        # return [word for word in word_list if detect_func(word)]
        return sum(1 for word in word_list if detect_func(word))

    def sentiment_analysis(self):
        sid = SentimentIntensityAnalyzer()
        sentiment = sid.polarity_scores(self.lyrics_string)
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


if __name__ == '__main__':
    filepath = "/Users/bar-study/PycharmProjects/genreReco/song_lyrics/21-savage-glock-in-my-lap.txt"
    lyrics_handler = LyricsHandler(filepath)

    # print(lyrics_handler.lyrics_string)
    # print(lyrics_handler.lyrics_lines)

    # wc = lyrics_handler.vers_chorus_count()
    # print(wc)

    sw = lyrics_handler.extract_lyrics_features()
    print(json.dumps(sw, indent=2))
    # is_slang = lyrics_handler.is_stop_word("it's")
    # print(is_slang)
    #
    # is_slang = lyrics_handler.is_slang_word("its")
    # print(is_slang)