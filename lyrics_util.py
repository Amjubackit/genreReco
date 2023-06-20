import requests
from bs4 import BeautifulSoup


def fetch_lyrics(artist, song_title):
    # Format the artist and song title for the URL
    artist = artist.lower().replace(" ", "-")
    song_title = song_title.lower().replace(" ", "-")
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

    # Return None if lyrics couldn't be fetched
    return None

