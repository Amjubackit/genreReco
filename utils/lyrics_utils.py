import json
import os
import re
import requests
from bs4 import BeautifulSoup
from nltk.corpus import words
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from utils.general_utls import is_file_valid, purify_text

# WORD_LIST = set(words.words())
STOPWORD_LIST = set(stopwords.words('english'))
SLANG_WORDS = [
    'stan', 'extra', 'cray', 'bae', 'goat', 'bet', 'giggin', 'noob', 'finesse', 'sus', 'mami', 'tryna'
                                                                                               'wanna', 'slay',
    'adorbs', 'gucci', 'flexin', 'chillin', 'squad', 'thicc', 'mad', 'fuego',
    'gig', 'finsta', 'salty', 'lituation', 'ratchet', 'frenemy', 'shade', 'suss', 'ghosting',
    'tea', 'viral', 'hella', 'highkey', 'tbt', 'wig', 'savage', 'gassed', 'slayin', 'mothafucka'
                                                                                    'shook', 'gang', 'swag', 'cap',
    'throw', 'clout', 'flossin', 'hangry', 'deadass', 'glo-up', 'yolo', 'clap', 'totes',
    'swerve', 'grind', "yall", 'dope', 'af', 'fomo', 'snatched', 'lil'
                                                                 'vibes', 'fleek', 'trill', 'grindin', 'lmao', 'slick',
    'drippin', 'ghosted', 'lowkey', 'swervin', 'rofl',
    'wavy', 'squad', 'catfish', 'thirst', 'bougie', 'dank', 'clutch', 'fit', 'snack',
    'lit', 'beef', 'boppin', 'swole', 'vibe', 'hype', 'woke', 'thirsty', 'gonna', 'fleek', 'baewatch', 'poppin'
]


class LyricsHandler:
    def __init__(self, lyrics_file):
        if not is_file_valid(lyrics_file):
            raise FileNotFoundError

        self.lyrics_raw = self.load_song_lyrics(lyrics_file)
        self.lyrics_lines = [line for line in self.lyrics_raw.split("\n") if line]
        self.clean_lyrics = self.clean_lyrics_string(" ".join(self.lyrics_lines))
        self.tokenized_lyrics = self.clean_lyrics.split()

    @staticmethod
    def load_song_lyrics(text_file):
        with open(text_file, 'r') as tf:
            string = tf.read()
        return string.lower()

    @staticmethod
    def clean_lyrics_string(string):
        string = re.sub(r'-', ' ', string)
        # Allow only letters, but remove anything inside a [] before to get rid of vers/chorus/singer names
        return re.sub(r'[^a-zA-Z\s\']', '', re.sub(r'\[.*?\]', '', string))

    @staticmethod
    def is_slang_word(word):
        return word.endswith("'") or word.startswith("'") or word.replace("'", "") in SLANG_WORDS

    @staticmethod
    def is_stop_word(word):
        return word.lower() in STOPWORD_LIST

    def intro_outro_vers_chorus_cnt(self):
        section_prefixes = ["intro", "outro", "verse", "chorus"]
        cnt_dict = {f"{prefix}_cnt": 0 for prefix in section_prefixes}
        for line in self.lyrics_lines:
            first_word = line.split(" ")[0]
            for prefix in section_prefixes:
                if first_word.startswith(f"[{prefix}"):
                    cnt_dict[f"{prefix}_cnt"] += 1
                    break

        return cnt_dict

    def count_words_by_type(self, word_type, unique=False):
        if word_type == "slang":
            return self.count_special_words(self.is_slang_word, unique)
        if word_type == "stop":
            return self.count_special_words(self.is_stop_word, unique)
        if word_type == "all":
            return len(self.clean_lyrics.split(" ")) if not unique else len(set(self.clean_lyrics.split(" ")))

    def count_special_words(self, detect_func, unique):
        word_list = self.tokenized_lyrics if not unique else set(self.tokenized_lyrics)
        # return [word for word in word_list if detect_func(word)]
        return sum(1 for word in word_list if detect_func(word))

    def sentiment_analysis(self):
        sid = SentimentIntensityAnalyzer()
        sentiment = sid.polarity_scores(self.clean_lyrics)
        return sentiment

    def extract_lyrics_features(self):
        word_count = self.count_words_by_type("all")
        unique_words = self.count_words_by_type("all", unique=True)
        stopword_count = self.count_words_by_type("stop")
        slang_word_count = self.count_words_by_type("slang")
        cnt_dict = self.intro_outro_vers_chorus_cnt()
        sentiment = self.sentiment_analysis()

        features = {
            "line_cnt": len(self.lyrics_lines),
            "word_cnt": word_count,
            "unique_words_ratio": round(unique_words / word_count, 3),
            "stop_words_ratio": round(stopword_count / word_count, 3),
            "slang_words_ratio": round(slang_word_count / word_count, 3),
            **cnt_dict,
            **sentiment
        }
        return features


def fetch_lyrics(url):
    # Format the artist and song title for the URL
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

# if __name__ == '__main__':
#     # filepath = "/Users/bar-study/PycharmProjects/genreReco/song_lyrics/eminem-superman.txt"
#     # lyrics_handler = LyricsHandler(filepath)
#     # print(lyrics_handler.clean_lyrics)
#     # print(lyrics_handler.tokenized_lyrics)
#     # slangs = [word for word in lyrics_handler.tokenized_lyrics if lyrics_handler.is_slang_word(word)]
#     # print(slangs)
#     # print(len(slangs))
#     print(len(SLANG_WORDS))
#     print(len(set(SLANG_WORDS)))
#     print(set(SLANG_WORDS))

#
#
# if __name__ == '__main__':
#     files = os.listdir("../song_lyrics")
#     for file in files:
#         if os.stat("../song_lyrics/" + file).st_size == 0:
#             print(f"REMOVING {file}")
#             os.remove("../song_lyrics/" + file)
