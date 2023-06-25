import re
import pandas as pd

from googleapiclient.discovery import build

import html
from unidecode import unidecode


def decode_html_entities(text):
    decoded_text = html.unescape(text)
    decoded_text = unidecode(decoded_text)
    return decoded_text

columns_removable = [
    "kind",
    "etag",
    "liveBroadcastContent",
    "publishTime",
    "publishedAt",
    "channelId",
    "thumbnails"
]


def split_song_title(song_title):
    """Sanitize YouTube video title to extract artist and track name

    Returns: (tuple) (artist, track name)
    """
    dbg = song_title
    # Remove anything after braces
    song_title = re.sub(r'\(.*', '', song_title.lower().strip())
    song_title = re.sub(r'\[.*', '', song_title.strip())
    song_title = re.sub(r'\|.*', '', song_title.strip())  # Remove everything after the pipeline character
    song_title = re.sub(r'[^a-zA-Z0-9\s-]', '', song_title.strip()) # Remove potentially leftover special chars
    if 'live' in song_title:
        print(f"supposed to remove live: '{song_title}' ('{dbg}')")
    song_title = re.sub(r'live performance$', '', song_title) # Remove potentially leftover special chars
    if not (
        song_title and
        len(re.findall(r' \- ', song_title)) == 1 and
        "," not in song_title):
        return

    # Split the song title into artist and song name
    try:
        artist, song_name = map(str.strip, song_title.split('-', 1))
    except Exception as e:
        print(f"{dbg,e}")
        raise e

    return {"artist":artist,"track":song_name}


def get_new_data(limit=None, pageToken=None, query=None):
    # Set your API key here
    api_key = "AIzaSyD75AnPSi95RfvfmWgO5Pt7laS1aplUq1o"

    # Set up the YouTube Data API
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Search for popular songs
    search_response = youtube.search().list(
        q=query or 'top hits', # dash means exclude
        part='snippet',
        type="video",
        videoDuration="short",
        order="viewCount",
        maxResults=limit or 100,
        pageToken=pageToken
    ).execute()

    # Extract relevant information from the search results
    items    = search_response.get('items', [])
    nextpage = search_response.get('nextPageToken')
    pageinfo = search_response.get('pageInfo')
    return items, nextpage, pageinfo

def items_to_df(items):
    df = pd.DataFrame(items)
    df = pd.concat(
        [
            df,
            df.pop('snippet').apply(pd.Series)
        ],
        axis=1)
    df["title"] = df["title"].apply(decode_html_entities)
    df = pd.concat(
        [
            df,
            df["title"].apply(split_song_title).apply(pd.Series)
        ],
        axis=1)

    df['videoId'] = df.pop("id").apply(pd.Series)["videoId"]
    df.drop(columns_removable, axis=1, inplace=True)
    return df
