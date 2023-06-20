import os

import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)
import nltk

# nltk.download('stopwords')
# nltk.download('punkt')
# nltk.download('cmudict')
# nltk.download('vader_lexicon')

from nltk.corpus import cmudict
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords


def load_song_lyrics(text_file):
    with open(text_file, 'r') as tf:
        lyrics = tf.read()

    return lyrics


def count_words(lyrics):
    words = word_tokenize(lyrics)
    return len(words)


def average_word_length(lyrics):
    words = word_tokenize(lyrics)
    total_length = sum(len(word) for word in words)
    return total_length / len(words) if len(words) > 0 else 0


def sentiment_analysis(lyrics):
    sid = SentimentIntensityAnalyzer()
    sentiment = sid.polarity_scores(lyrics)
    return sentiment


def find_rhymes_count(lyrics):
    pronunciations = cmudict.dict()
    words = word_tokenize(lyrics.lower())
    unique_words = set(words)

    rhymes_count = 0
    for word in unique_words:
        try:
            phonemes = pronunciations[word]
        except KeyError:
            continue
        rhyming_words = []
        for rhyme_word, rhyme_phonemes in pronunciations.items():
            if rhyme_word != word and rhyme_phonemes[-2:] == phonemes[-2:]:
                rhyming_words.append(rhyme_word)
        rhymes_count += len(rhyming_words)

    return rhymes_count


def extract_lyrics_info(song_lyrics):
    lyrics_info = []
    verse_num = 0
    chorus_num = 0
    stopwords_list = set(stopwords.words('english'))

    lines = song_lyrics.split('\n')
    lines_count = len(lines)
    lyrics_text = ' '.join(lines)  # Combine all lines into a single string

    word_count = count_words(lyrics_text)
    avg_word_length = average_word_length(lyrics_text)
    # sentiment = sentiment_analysis(lyrics_text)
    rhymes = find_rhymes_count(song_lyrics)
    rhymes_perc = round(rhymes / word_count, 2)
    stopwords_count = sum(1 for word in word_tokenize(lyrics_text) if word.lower() in stopwords_list)

    for line in lines:
        line = line.strip()
        if line.startswith("[Chorus"):
            chorus_num += 1
        elif line.startswith("[Verse"):
            verse_num += 1

    lyrics_info.append(
        [lines_count, word_count, avg_word_length, rhymes, rhymes_perc, chorus_num, verse_num, stopwords_count])
    return lyrics_info


# Example usage
songs_dir = "song_lyrics"
filenames = next(os.walk(songs_dir), (None, None, []))[2]
columns = [
    'Line count',
    'Word Count',
    'Average Word Length',
    'Rhymes',
    'Rhymes Percentage',
    'Chorus Number',
    'Verse Number',
    'Stopwords Count'
]
for filename in filenames:
    file_path = os.path.join(songs_dir, filename)
    lyrics = load_song_lyrics(file_path)
    lyrics_info = extract_lyrics_info(lyrics)
    df = pd.DataFrame(lyrics_info, columns=columns)
    print(df)
