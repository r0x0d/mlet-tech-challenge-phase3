# prompt: Now, generate the complete code for me with spotipy credentials variables and right scope

import pickle
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import numpy as np

# Create a Spotify client
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id="",
        client_secret="",
        redirect_uri="http://example.com",
        scope="playlist-read-private playlist-modify-private user-library-read user-read-private",
    )
)

MODEL = None
with open("model.pkl", mode="rb") as f:
    MODEL = pickle.load(f)


# Assuming you have a pre-trained model named 'model'
# Replace this with your actual model loading and prediction code
def predict_popularity(audio_features):
    # Replace this with your actual prediction logic
    # Example:
    # input_features = np.array([audio_features['danceability'], audio_features['energy'], ...])
    # popularity = model.predict([input_features])[0]
    # return popularity
    return 0.5  # Placeholder


st.title("Spotify Playlist Viewer")

audio_features_dict = {}  # Dictionary to store audio features

try:
    playlists = sp.current_user_playlists()
    st.write("Your Playlists:")

    playlist_options = []
    for playlist in playlists["items"]:
        playlist_options.append(playlist["name"])

    selected_playlists = st.multiselect(
        "Select up to 4 playlists:", playlist_options, max_selections=4
    )

    if selected_playlists:
        st.write(f"You selected: {', '.join(selected_playlists)}")

    for playlist_name in selected_playlists:
        # Find the playlist ID based on the selected name
        playlist_id = None
        for playlist in playlists["items"]:
            if playlist["name"] == playlist_name:
                playlist_id = playlist["id"]
                break

        if playlist_id:
            try:
                results = sp.playlist_items(playlist_id)
                st.write(f"## Music in {playlist_name}: {len(results['items'])}")

                with st.spinner("Extracting audio features..."):
                    for item in results["items"]:
                        track = item["track"]
                        track_id = track["id"]
                        # Extract audio features
                        try:
                            audio_features = sp.audio_features(track_id)[0]
                            if audio_features:
                                audio_features_dict[track_id] = audio_features
                        except Exception as e:
                            st.warning(
                                f"Could not extract audio features for {track['name']}: {e}"
                            )
            except Exception as e:
                st.error(f"Error fetching music for {playlist_name}: {e}")
        else:
            st.warning(f"Could not find the playlist ID for {playlist_name}")

    if audio_features_dict:
        st.write("## Audio Features:")
        popularity_filter = st.radio(
            "Filter by Popularity:",
            ["All", "High (70+)", "Medium (40-69)", "Low (0-39)"],
        )

except Exception as e:
    st.error(f"Error fetching playlists: {e}")
