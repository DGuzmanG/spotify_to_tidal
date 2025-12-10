import spotipy
from spotipy.oauth2 import SpotifyOAuth
import tidalapi
import yaml
from pathlib import Path

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
session = tidalapi.Session()
session.login_oauth_simple()

# Get Spotify playlist
print("Fetching Spotify playlist...")
playlist_id = '2Dy2i11OlwIzpUZkC8Y8p6'
spotify_tracks = []
results = sp.playlist_tracks(playlist_id)
spotify_tracks.extend(results['items'])
while results['next']:
    results = sp.next(results)
    spotify_tracks.extend(results['items'])

# Create clean list
spotify_songs = []
for idx, item in enumerate(spotify_tracks, 1):
    track = item['track']
    if track:
        spotify_songs.append({
            'position': idx,
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'album': track['album']['name']
        })

print(f"Spotify: {len(spotify_songs)} tracks")

# Get Tidal playlist
print("Fetching Tidal playlist...")
user_playlists = session.user.playlists()
tidal_playlist = None
for p in user_playlists:
    if "Dave's Brain" in p.name:
        tidal_playlist = p
        break

tidal_songs = []
if tidal_playlist:
    tidal_tracks = tidal_playlist.tracks()
    for t in tidal_tracks:
        tidal_songs.append({
            'name': t.name,
            'artist': t.artist.name,
            'album': t.album.name if hasattr(t, 'album') else 'Unknown'
        })
    
    print(f"Tidal: {len(tidal_songs)} tracks")
else:
    print("Couldn't find Tidal playlist!")
    exit()

# Compare - check if each Spotify song is in Tidal
print("\n" + "="*80)
print("MISSING SONGS (In Spotify but NOT in Tidal):")
print("="*80)

missing = []
for song in spotify_songs:
    # Check if song exists in Tidal (fuzzy match on name + artist)
    found = False
    for tidal_song in tidal_songs:
        # Normalize for comparison
        spotify_name = song['name'].lower().strip()
        spotify_artist = song['artist'].lower().strip()
        tidal_name = tidal_song['name'].lower().strip()
        tidal_artist = tidal_song['artist'].lower().strip()
        
        # Match if name and artist are the same
        if spotify_name == tidal_name and spotify_artist == tidal_artist:
            found = True
            break
    
    if not found:
        missing.append(song)
        print(f"\n{len(missing)}. {song['name']}")
        print(f"   Artist: {song['artist']}")
        print(f"   Album: {song['album']}")
        print(f"   Position in Spotify: #{song['position']}")

print("\n" + "="*80)
print(f"SUMMARY: {len(missing)} songs missing from Tidal")
print("="*80)

# Save to file
with open('missing_songs.txt', 'w', encoding='utf-8') as f:
    f.write(f"Missing Songs Report\n")
    f.write(f"={'='*60}\n\n")
    f.write(f"Spotify playlist: {len(spotify_songs)} tracks\n")
    f.write(f"Tidal playlist: {len(tidal_songs)} tracks\n")
    f.write(f"Missing: {len(missing)} tracks\n\n")
    f.write(f"{'='*60}\n\n")
    
    for idx, song in enumerate(missing, 1):
        f.write(f"{idx}. {song['name']} - {song['artist']}\n")
        f.write(f"   Album: {song['album']}\n")
        f.write(f"   Spotify Position: #{song['position']}\n\n")

print(f"\nDetailed report saved to: missing_songs.txt")
