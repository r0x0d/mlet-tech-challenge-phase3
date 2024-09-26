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


def load_model():
    with open("model.pkl", mode="rb") as f:
        model = pickle.load(f)
        return model


def main():
    st.title("Recomendação de músicas populares no Spotify!")

    playlists = sp.current_user_playlists()
    st.write("Suas playlists:")

    playlist_options = [playlist["name"] for playlist in playlists["items"]]
    selected_playlists = st.multiselect(
        "Selecione até 4 playlists:", playlist_options, max_selections=4
    )
    st.write("## Filtro por popularidade:")
    popularity_filter = st.selectbox(
        "Filtro por popularidade:",
        ["Alta (70+)", "Média (40-69)", "Baixa (0-39)"],
        index=1,
    )

    playlist_dict = {}

    if selected_playlists:
        playlist_dict = {
            playlist["id"]: {"name": playlist["name"], "tracks": []}
            for playlist in playlists["items"]
            if playlist["name"] in selected_playlists
        }

    if st.button("Analisar playlsits"):
        for playlist_id, data in playlist_dict.items():
            st.write(f"## Playlist analisada: '{data['name']}'")

            results = sp.playlist_items(playlist_id)
            playlist_dict[playlist_id]["tracks"] = results["items"]

        tracks_with_audio_features = {}
        with st.spinner("Extraindo audio features..."):
            track_ids = []
            for item in playlist_dict.values():
                tracks = item["tracks"]
                track_ids = [track["track"]["id"] for track in tracks]

            try:
                time.sleep(0.2)
                audio_features = sp.audio_features(track_ids)
                for track_id, audio_feature in zip(track_ids, audio_features):
                    tracks_with_audio_features[track_id] = [audio_feature]
            except Exception as e:
                st.warning(f"Could not extract audio features: {e}")

        filtered_tracks = []
        for (
            track_id,
            audio_feature,
        ) in tracks_with_audio_features.items():
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
            model = load_model()
            popularity = model.predict(features)[0]
            if popularity_filter == "Alta (70+)":
                if popularity >= 70:
                    filtered_tracks.append(track_id)
            elif popularity_filter == "Média (40-69)":
                if 40 <= popularity <= 69:
                    filtered_tracks.append(track_id)
            elif popularity_filter == "Baixa (0-39)":
                if popularity <= 39:
                    filtered_tracks.append(track_id)

        user_id = sp.current_user()["id"]
        new_playlist = sp.user_playlist_create(
            user=user_id,
            name="Spotify Recommended Playlist - MLET",
            description="Playlist criada com base em suas playlists.",
            public=False,
        )
        playlist_id = new_playlist["id"]

        # Add the filtered tracks to the new playlist
        sp.playlist_add_items(playlist_id, filtered_tracks)
        st.success(
            "Nova playlist 'Spotify Recommended Playlist - MLET' criada com sucesso!"
        )


if __name__ == "__main__":
    main()
