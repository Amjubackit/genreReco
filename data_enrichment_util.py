import difflib
import requests
from bs4 import BeautifulSoup


def find_longest_matching_string(href_list, given_string):
    longest_match = None  # (Value, match)
    for href in href_list:
        normalized_href = href.lower()
        normalized_given_string = given_string.lower()
        sequence_matcher = difflib.SequenceMatcher(None, normalized_href, normalized_given_string)
        match = sequence_matcher.find_longest_match(0, len(normalized_href), 0, len(normalized_given_string))
        if longest_match is None or match.size >= len(longest_match[1]) and len(href)-match.size < len(longest_match[0])-len(longest_match[1]):
            longest_match = (href, href[match.a:match.a+match.size])
    if longest_match is None:
        return
    return longest_match[0]


def get_valid_mask(df):
    return df["title"].apply(lambda x: " - "  in x and "," not in x)


def get_soup_by_url(url):
    response = requests.get(url)
    # Check if the request was successful
    try:
        response.raise_for_status()
    except:
        print(f"ERROR: {url}")
        return

    return BeautifulSoup(response.content, 'html.parser')


def name_to_url(s, custom_replace=None):
    """Generic function to convert a song artist/track name to a url-valid string
    Supports customizing replacements, such as adding behaviour, or changing default behaviour
    returns: Sanitized string after replacements
    """
    replacers = {
        '"': '',
        '+': '',
        '  ': ' ',
        "'": '-',
        "?": '',
        '’': '-'
    }
    if custom_replace:
        replacers.update(custom_replace)

    for k,v in replacers.items():
        s = s.replace(k,v)
    return s.replace(' ', '-')


def fetch_lyrics(artist, song_title):
    lyrics_lines = None
    try:
        genius_replace = {
                '.':'',
                "'": '',
                ',':'',
                '’': ''
            }
        # Format the artist and song title for the URL
        artist = name_to_url(artist, custom_replace=genius_replace )
        song_title = name_to_url(
            song_title,
            custom_replace=genius_replace)
        genius_url = "https://genius.com"
        pattern = f"{genius_url}/{artist}-{song_title}-lyrics"
        soup = get_soup_by_url(pattern)
        if not soup:
            if not soup:
                print(f"ERROR: {artist, song_title, pattern}")
                raise RuntimeError("No soup for you")

        # Find the lyrics section
        lyrics_divs = soup.find_all('div', attrs={"data-lyrics-container":"true"})

        lyrics_lines = [
            d.get_text('\n') # Replace HTML-<br> with newline
            for d in lyrics_divs # iterate over divs by original order
        ]
    except Exception as e:
        print("Exception caught", e)
    finally:
        return {"lyrics_lines":lyrics_lines}


def get_from_page(key, page_object):
    dds_list = page_object.find_all("dd")
    txt_list = []   # DEBUG, NOT BUSINESS LOGIC
    for dd in dds_list:
        all_txt = dd.get_text()

        txt_list.append(all_txt)  # DEBUG, NOT BUSINESS LOGIC

        ptext = dd.parent.contents[0].get_text()
        if key not in ptext:
            continue
        break
    else:
        print("Error", *txt_list)  # DEBUG, NOT BUSINESS LOGIC
        return
    return dd.contents[0].get_text()


def get_song_data(artist, song_title):
    try:
        print(f"querying {artist, song_title}")
        tempo    = None
        key      = None
        duration = None
        songbpm_url = "https://songbpm.com"
        pattern = f"{songbpm_url}/@{name_to_url(artist)}/{name_to_url(song_title)}"
        page_object = get_soup_by_url(pattern)
        if not page_object:
            # Try fallback, search and query best match
            # Details about songbpm:
            # - In order to search you POST your query
            # - in return you get a query ID (id and href)
            # - then need to search and get as HTML
            search_resp = requests.post(f"{songbpm_url}/api/search", json={"query":f"{artist} {song_title}"}, headers={"Content-Type":"application/json"})
            href = search_resp.json()["data"]["href"]
            search_soup = get_soup_by_url(f"{songbpm_url}{href}")
            hrefs = [tag.get('href') for tag in search_soup.find_all('a', class_="items-start") ]

            fallback = find_longest_matching_string(hrefs, pattern)
            page_object = get_soup_by_url(f"{songbpm_url}{fallback}")
            if not page_object:
                print(f"ERROR: {artist, song_title, pattern}")
                return
            print(f"WARNING: Using different URL: {fallback} (not {pattern})")

        tempo    = get_from_page("Tempo", page_object)
        key      = get_from_page("Key", page_object)
        duration = get_from_page("Duration", page_object)
    except Exception as e:
        print(f"I crashed {artist, song_title}")
    finally:
        return {"tempo": tempo, "key": key, "duration":duration}
