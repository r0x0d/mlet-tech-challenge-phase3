# prompt: Now, generate the complete code for me with spotipy credentials variables and right scope
import json
import time
import pickle
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd

# Create a Spotify client
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id="",
        client_secret="",
        redirect_uri="http://example.com",
        scope="playlist-read-private playlist-modify-private user-library-read user-read-private",
    )
)

tracks_with_audio_features = {}
playlist_dict = {}

MODEL = None
with open("model.pkl", mode="rb") as f:
    MODEL = pickle.load(f)

st.title("Spotify Playlist Viewer")

try:
    playlists = sp.current_user_playlists()
    st.write("Your Playlists:")

    playlist_options = [playlist["name"] for playlist in playlists["items"]]

    selected_playlists = st.multiselect(
        "Select up to 2 playlists:", playlist_options, max_selections=2
    )

    if selected_playlists:
        playlist_dict = {
            playlist["id"]: {"name": playlist["name"], "tracks": []}
            for playlist in playlists["items"]
            if playlist["name"] in selected_playlists
        }

    if playlist_dict:
        for playlist_id, data in playlist_dict.items():
            st.write(f"## Analisando playlist '{data['name']}'")

            try:
                results = sp.playlist_items(playlist_id)
                playlist_dict[playlist_id]["tracks"] = results["items"]
            except Exception as e:
                st.error(f"Error fetching music for {data['name']}: {e}")

    if st.button("Extrair audio features"):
        with st.spinner("Extraindo audio features..."):
            track_ids = []
            for item in playlist_dict.values():
                tracks = item["tracks"]
                track_ids = [track["track"]["id"] for track in tracks]

            # Extract audio features
            try:
                time.sleep(0.2)
                audio_features = sp.audio_features(track_ids)
                for track_id, audio_feature in zip(track_ids, audio_features):
                    tracks_with_audio_features[track_id] = [audio_feature]
            except Exception as e:
                st.warning(f"Could not extract audio features: {e}")

            print(tracks_with_audio_features)

    if tracks_with_audio_features:
        st.write("## Filtro por popularidade:")
        popularity_filter = st.selectbox(
            "Filter by Popularity:",
            ["High (70+)", "Medium (40-69)", "Low (0-39)"],
        )

        if popularity_filter:
            if st.button("Criar playlist com novas músicas"):
                new_playlist_name = st.text_input("Enter a name for your new playlist:")
                new_playlist_description = st.text_input(
                    "Enter the description of your new playlist:"
                )

                if new_playlist_name:
                    filtered_tracks = []
                    for track_id, audio_feature in tracks_with_audio_features.items():
                        audio_feature_pd = pd.DataFrame(audio_feature)
                        features = audio_feature_pd[
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
                        if popularity_filter == "High (70+)":
                            popularity = MODEL.predict(features)[0]
                            if popularity >= 70:
                                filtered_tracks.append(track_id)
                        elif popularity_filter == "Medium (40-69)":
                            popularity = MODEL.predict(features)[0]
                            if 40 <= popularity <= 69:
                                filtered_tracks.append(track_id)
                        elif popularity_filter == "Low (0-39)":
                            popularity = MODEL.predict(features)[0]
                            if popularity <= 39:
                                filtered_tracks.append(track_id)

                        user_id = sp.current_user()["id"]
                        new_playlist = sp.user_playlist_create(
                            user=user_id,
                            name=new_playlist_name,
                            description=new_playlist_description,
                            public=False,
                        )
                        playlist_id = new_playlist["id"]

                        # Add the filtered tracks to the new playlist
                        sp.playlist_add_items(playlist_id, filtered_tracks)
                        st.success(
                            f"New playlist '{new_playlist_name}' created with filtered tracks!"
                        )
except Exception as e:
    st.error(f"Error fetching playlists: {e}")
