import pickle
import pandas
import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = "user-library-read"

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope=scope,
        client_id="0bfc6875b7eb45e6bc2166c88b7df8a6",
        client_secret="f2ed74f9776a4cdb958e14b1ed35620f",
        redirect_uri="http://example.com",
    )
)

PLAYLIST_SONGS_POPULARITY = {}
DROP_AUDIO_FEATURES_COLUMNS = ["id", "type", "uri", "track_href", "analysis_url"]
loaded_model = None
with open("model.pkl", mode="rb") as f:
    loaded_model = pickle.load(f)

results = sp.playlist("3ZgmfR6lsnCwdffZUan8EA")
for track in results["tracks"]["items"]:
    track_id = track["track"]["id"]
    audio_features = sp.audio_features(track_id)[0]
    _ = [audio_features.pop(column) for column in DROP_AUDIO_FEATURES_COLUMNS]
    dataset = pandas.DataFrame([audio_features])
    X = dataset[
        [
            "duration_ms",
            "danceability",
            "energy",
            "key",
            "loudness",
            "mode",
            "speechiness",
            "acousticness",
            "instrumentalness",
            "liveness",
            "valence",
            "tempo",
            "time_signature",
        ]
    ]
    pred = loaded_model.predict(X)
    if pred[0] > 45:
        print(pred)
    PLAYLIST_SONGS_POPULARITY[track_id] = {"prob": pred[0]}

print(PLAYLIST_SONGS_POPULARITY)