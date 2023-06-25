import json

import pandas as pd
from os import environ

import data_enrichment_util as dutil
import youtube_util as ytutil


# MUSIC_API_TOKEN="2cf82db3-4064-4235-8253-16994eb51773"
# def make_musicapi_call():
#     r = requests.Request("POST",
#                          headers={
#                             "Authorization": f"Token {MUSIC_API_TOKEN}",
#                             "Content-Type": "application/json; charset=utf-8"
#                          },
#                          url="https://api.musicapi.com/search",
#                          json={
#                              "track":"Bring Me To Life",
#                              "type":"track",
#                              "sources":["spotify", 'youtube']})
#     return r

base_cols = ["artist", "track"]


def debug(msg):
    if not int(environ.get("DEBUG", 0)):
        return
    print(f"DEBUG: {msg}")


def enrich(df, extend_df=None, **kwargs):
    # Default behavior when nothing specified is to do all
    get_all = False
    if len(kwargs.keys()) == 0:
        get_all = True
    if get_all or 'data' in kwargs:
        df = df.combine_first(df.apply(lambda x: dutil.get_song_data(*x[base_cols]), axis=1).apply(pd.Series))
    if get_all or 'lyrics' in kwargs:
        df["lyrics_lines"] = df.apply(lambda x: dutil.fetch_lyrics(*x[base_cols]), axis=1).apply(pd.Series)
    if extend_df is not None:
        df = extend_df.combine_first(
            df
        )
    return df
# df = pd.concat([df, df.apply(lambda x: dutil.get_song_data(*x[base_cols]), axis=1).apply(pd.Series)], axis=1)

def rename_me(use_cache, enrich, limit=None):
    fname_df='data-df.json'
    if use_cache:
        df = pd.read_json(fname_df)
    else:
        # Extract relevant information from the search results
        df = ytutil.items_to_df(ytutil.get_new_data(limit=limit)[0])

    if enrich:
        df = enrich(df)
    df.to_json(fname_df)
    return df

def main():
    use_cache =  int(environ.get("USE_CACHE", "1"))
    enrich =  int(environ.get("ENRICH", "1"))
    df = rename_me(use_cache, enrich, 4)
    print(f"Got {len(df)} items. {df.columns=}")
    print(df)

if __name__ == "__main__":
    main()
