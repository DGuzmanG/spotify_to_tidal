import spotipy
from spotipy.oauth2 import SpotifyOAuth
import tidalapi
import yaml

# Load config
with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)

# Spotify setup
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=config['spotify']['client_id'],
    client_secret=config['spotify']['client_secret'],
    redirect_uri=config['spotify']['redirect_uri'],
    scope='user-library-read playlist-read-private'
))

# Tidal setup
# Tidal setup
session = tidalapi.Session()
session.login_oauth_simple()

# Get Spotify playlist
playlist_id = '2Dy2i11OlwIzpUZkC8Y8p6'
spotify_tracks = []
results = sp.playlist_tracks(playlist_id)
spotify_tracks.extend(results['items'])
while results['next']:
    results = sp.next(results)
    spotify_tracks.extend(results['items'])

print(f"Spotify tracks: {len(spotify_tracks)}")

# Get Tidal playlist
user_playlists = session.user.playlists()
tidal_playlist = None
for p in user_playlists:
    if "Dave's Brain" in p.name:
        tidal_playlist = p
        break

if tidal_playlist:
    tidal_tracks = tidal_playlist.tracks()
    print(f"Tidal tracks: {len(tidal_tracks)}")
    
    # Find missing songs
    tidal_track_ids = {(t.name.lower(), t.artist.name.lower()) for t in tidal_tracks}
    
    missing = []
    for item in spotify_tracks:
        track = item['track']
        if track:
            name = track['name'].lower()
            artist = track['artists'][0]['name'].lower()
            if (name, artist) not in tidal_track_ids:
                missing.append(f"{track['name']} - {track['artists'][0]['name']}")
    
    print(f"\nMissing {len(missing)} songs:")
    for song in missing[:10]:  # Show first 10
        print(f"  - {song}")
