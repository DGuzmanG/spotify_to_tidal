import spotipy
from spotipy.oauth2 import SpotifyOAuth
import yaml

# Load config
with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)

# Auth
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=config['spotify']['client_id'],
    client_secret=config['spotify']['client_secret'],
    redirect_uri=config['spotify']['redirect_uri'],
    scope='user-library-read playlist-read-private'
))

# Get playlist
playlist_id = '2Dy2i11OlwIzpUZkC8Y8p6'
results = sp.playlist_tracks(playlist_id)
tracks = results['items']

# Get all tracks (handle pagination)
while results['next']:
    results = sp.next(results)
    tracks.extend(results['items'])

print(f"Total tracks from Spotify API: {len(tracks)}")

# Check for None tracks
none_count = sum(1 for t in tracks if t['track'] is None)
print(f"Tracks with None/null data: {none_count}")

# Check for local tracks
local_count = sum(1 for t in tracks if t['track'] and t['track'].get('is_local', False))
print(f"Local tracks: {local_count}")

# Check for unavailable
unavailable = sum(1 for t in tracks if t['track'] and not t['track'].get('is_playable', True))
print(f"Unavailable tracks: {unavailable}")

print(f"\nValid streaming tracks: {len(tracks) - none_count - local_count}")
