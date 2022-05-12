# Imports
import os

from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Spotify API information
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REDIRECT_UI = "http://example.com"
OAUTH_TOKEN = "https://accounts.spotify.com/api/token"

# Allow user input
user_year = input("What year would you like to travel to? Type it in the format YYYY-MM-DD\n")

# Gather the data from the website
URL = "https://www.billboard.com/charts/hot-100/" + user_year
response = requests.get(URL).text

soup = BeautifulSoup(response, "html.parser")

only_artists = []
only_songs = []

# Find all songs on the web page using bs4
all_titles = soup.find_all("h3", {"id": "title-of-a-story", "class": "a-no-trucate"})

for song in all_titles:
    only_songs.append(song.getText())
    # Artist is in the span tag directly after the song title
    artist = song.find_next('span').getText()
    only_artists.append(artist)

# Connect to spotify API
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri=REDIRECT_UI,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        show_dialog=True,
        cache_path="token.txt"
    )
)

user_id = sp.current_user()["id"]
year = user_year.split("-")[0]
song_uris = []
for song in only_songs:
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    # Use try except to catch songs that aren't on spotify
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} is not on Spotify.")

# Create the Initial playlist
playlist = sp.user_playlist_create(user_id, f"{user_year} Billboard 100", public=False, description="This playlist was created using BeautifulSoup4!")

# Add all available songs to playlist
sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)

print("Your playlist has been created, go give it a listen!")
