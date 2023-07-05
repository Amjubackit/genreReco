import json
import os
import os.path as osp
import re
import requests
from bs4 import BeautifulSoup
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from utils.general_utls import is_file_valid
slang_file_path = osp.join(osp.dirname(osp.abspath(__file__)), 'slang_words.txt')

STOPWORD_LIST = set(stopwords.words('english'))
SLANG_WORDS = []
with open(slang_file_path, 'r') as file:
    [SLANG_WORDS.append(line.strip()) for line in file]


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
            for prefix in section_prefixes:
                if f"[{prefix}" in line:
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
            **cnt_dict,
            "line_cnt": len(self.lyrics_lines),
            "word_cnt": word_count,
            "unique_word_cnt": unique_words,
            "stop_word_cnt": stopword_count,
            "slang_word_cnt": slang_word_count,
            "positive": sentiment.get("pos"),
            "negative": sentiment.get("neg"),
            "neutral": sentiment.get("neu"),
            "compound": sentiment.get("compound"),
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
        lyrics_lines =[]
        for d in lyrics_divs:
            [lb.replaceWith('\n') for lb in d.findAll('br')]

            lines = re.sub('\n{2,}', '\n', d.getText().strip())
            lyrics_lines.append(lines)

        return lyrics_lines

    print(f"Lyrics data not found")
    # Return None if lyrics couldn't be fetched
    return None


def save_lyrics(txt, file_path):
    with open(file_path, 'w') as file:
        file.write(txt)


def get_lyrics_and_save(genius_url, lyrics_file):
    lyrics = fetch_lyrics(genius_url)
    if not lyrics:
        print("RETURNS PARTIAL DATA DUE TO LYRICS FETCH FAILURE")
        return

    save_lyrics('\n'.join(lyrics), lyrics_file)

    print(f"INIT HANDLER FOR FILE: {lyrics_file}")
    lyrics_handler = LyricsHandler(lyrics_file)
    lyrics_features = lyrics_handler.extract_lyrics_features()
    return lyrics_features


def reget_lyrics_df(dataset):
    for index, row in dataset.iterrows():
        record = row.copy()
        f = get_lyrics_and_save(record.lyrics_url, record.lyrics_file)
        record.update(f)
        dataset.loc[index] = record

    return dataset