import streamlit as st
from streamlit_option_menu import option_menu
import urllib.parse
import pandas as pd
from auth import get_access_token
from spotify_api import get_user_queue, get_artist_genres, get_user_profile
from collections import Counter
from playlist_analysis import PlaylistAnalyzer
from analytic import Recommender
from dotenv import load_dotenv
from imdb_movie_poster import get_poster_url_by_title
import plotly.express as px
import requests
import time
import os

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID") or st.secrets.get("SPOTIFY_CLIENT_ID")
REDIRECT_URI = "https://music2movie.streamlit.app/"
SCOPE = "user-read-email user-read-private user-read-playback-state user-top-read"

# Giriş URL'si oluştur
params = {
    "client_id": CLIENT_ID,
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
}
auth_url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(params)

def home_page(queue_data):

    selected = option_menu(
        menu_title=None,
        options=["Queue Songs", "Playlists"],
        icons=["music-note", "film"],
        orientation="horizontal",
        styles={
            "icon": {"color": "white", "font-size": "18px"},
            "nav-link-selected": {
                "background-color": "#9B090E",
                "font-weight": "bold",
                "color": "white",
            },
        }
    )

    main_col, movie_col = st.columns([1, 2])

    if selected == "Queue Songs":
        if "queue" in queue_data:
            with main_col:
                st.markdown("### 🎶 Queue Songs")
                with st.container(height=500, border=True):
                    if queue_data.get("queue"):
                        for track in queue_data["queue"]:
                            song_name = track["name"]
                            album_image = track["album"]["images"][0]["url"]
                            artist_list = track["artists"]
                            artist_ids = [artist["id"] for artist in artist_list]
                            artist_count = len(artist_ids)

                            all_genres = []
                            for artist_id in artist_ids:
                                genres = get_artist_genres(artist_id, access_token)
                                all_genres.extend(genres)
                                genre_counts.update(genres)

                            all_genres = list(set(all_genres)) or ["(No genres)"]

                            with st.container():
                                cols = st.columns([1, 3])
                                with cols[0]:
                                    st.image(album_image, width=100)
                                with cols[1]:
                                    st.markdown(f"### 🎵 {song_name}")
                                    st.markdown(f"👥 **Number of Artist:** {artist_count}")
                                    st.markdown(f"🎼 **Genres:** {', '.join(all_genres)}")
                            st.divider()
                    else:
                        st.error("There are no songs in your Spotify queue at the moment.")

                    if genre_counts:
                        most_common_genre = genre_counts.most_common(1)[0][0]
                    else:
                        most_common_genre = "NotValid"

            with movie_col:
                st.markdown(f"### 🎬 Movie Suggestion ({most_common_genre})")
                result = recommender.recommend_varied_films(most_common_genre)
                print("FOUNDED GENRE: " + str(most_common_genre))
                print("DEBUG_ML: \n" + str(result))
                with st.container(height=500, border=True):
                    for i, row in result.iterrows():
                        with st.container():
                            col1, col2 = st.columns([1, 3])
                            with col1:
                                poster_url = get_poster_url_by_title(row['title'])
                                if poster_url and poster_url != "N/A":
                                    st.image(poster_url, use_container_width=True)
                                else:
                                    st.image("image/Netflix_icon.svg", use_container_width=True)
                            with col2:
                                st.markdown(f"### {row['title']}")
                                st.markdown(f"- ⭐ IMDb: {row['vote_average']}")
                                if not pd.isna(row.get("emotion_score")):
                                    st.markdown(f"- 🎭 Emotion Score: {row['emotion_score']}")
                                    st.markdown(f"- 🧠 Final Score: {row['final_score']:.2f}")
                            st.markdown("---")

    if selected == "Playlists":
        analyzer = PlaylistAnalyzer(access_token)
        all_playlists = analyzer.get_all_playlists()

        if all_playlists:
            top_playlists = analyzer.get_top_playlists(all_playlists)

            if not top_playlists:
                st.error("No playlist with enough songs was found.")
            else:
                genres, playlist_summaries = analyzer.analyze_genres_from_playlists(top_playlists)
                genre_counts.update(genres)

                st.session_state.top_playlists = top_playlists
                st.session_state.genres = genres
                st.session_state.playlist_summaries = playlist_summaries
                st.session_state.genre_counts = genre_counts

                most_common_genre = genre_counts.most_common(1)[0][0]
                st.markdown(f"🎧 Founded Genre: **{most_common_genre}**")

            if not top_playlists:
                st.session_state.top_playlists = []
                st.session_state.genres = {}
                st.session_state.playlist_summaries = []
                st.session_state.genre_counts = Counter()
        else:
            most_common_genre = "NotValid"

        with main_col:
            st.markdown("### 🎼 Playlists")
            with st.container(height=500, border=True):
                if not all_playlists:
                    st.error("🎵 You don’t have any playlists to analyze.")
                else:
                    for playlist in playlist_summaries:
                        name = playlist["name"]
                        image = playlist["image"]
                        track_count = playlist["track_count"]

                        with st.container():
                            cols = st.columns([1, 3])
                            with cols[0]:
                                st.image(image, width=100)
                            with cols[1]:
                                st.markdown(f"### 📀 {name}")
                                st.markdown(f"🎵 **Number of Songs:** {track_count}")
                        st.divider()
        with movie_col:
            st.markdown(f"### 🎬 Movie Suggestion ({most_common_genre})")
            result = recommender.recommend_varied_films(most_common_genre)
            print("FOUNDED GENRE: " + str(most_common_genre))
            print("DEBUG_ML: \n" + str(result))
            with st.container(height=500, border=True):
                for i, row in result.iterrows():
                    with st.container():
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            poster_url = get_poster_url_by_title(row['title'])
                            if poster_url and poster_url != "N/A":
                                st.image(poster_url, use_container_width=True)
                            else:
                                st.image("image/Netflix_icon.svg", use_container_width=True)
                        with col2:
                            st.markdown(f"### {row['title']}")
                            st.markdown(f"- ⭐ IMDb: {row['vote_average']}")
                            if not pd.isna(row.get("emotion_score")):
                                st.markdown(f"- 🎭 Emotion Score: {row['emotion_score']}")
                                st.markdown(f"- 🧠 Final Score: {row['final_score']:.2f}")
                        st.markdown("---")


def developer_mode(queue_data):
    selected = option_menu(
        menu_title=None,
        options=["Queue Songs", "Playlists"],
        icons=["music-note", "film"],
        orientation="horizontal",
        styles={
            "icon": {"color": "white", "font-size": "18px"},
            "nav-link-selected": {
                "background-color": "#9B090E",
                "font-weight": "bold",
                "color": "white",
            },
        }
    )

    if selected == "Queue Songs":
        # Eğer şarkı verisi varsa, detayları göster
        if "queue" in queue_data:
            main_col, chart_col, genre_col = st.columns([1, 1, 1])

            with main_col:
                st.markdown("### 🎶 Queue Songs")

                with st.container(height=500, border=True):
                    if queue_data.get("queue"):
                        for track in queue_data["queue"]:
                            song_name = track["name"]
                            album_image = track["album"]["images"][0]["url"]
                            artist_list = track["artists"]
                            artist_ids = [artist["id"] for artist in artist_list]
                            artist_count = len(artist_ids)

                            all_genres = []
                            for artist_id in artist_ids:
                                genres = get_artist_genres(artist_id, access_token=access_token)
                                all_genres.extend(genres)
                                genre_counts.update(genres)

                            all_genres = list(set(all_genres)) or ["(No genres)"]

                            with st.container():
                                cols = st.columns([1, 3])
                                with cols[0]:
                                    st.image(album_image, width=100)
                                with cols[1]:
                                    st.markdown(f"### 🎵 {song_name}")
                                    st.markdown(f"👥 **Number of Artist:** {artist_count}")
                                    st.markdown(f"🎼 **Genres:** {', '.join(all_genres)}")
                            st.divider()
                    else:
                        st.error("There are no songs in your Spotify queue at the moment.")

            with chart_col:
                st.markdown("### 🍰 Genre Chart")
                with st.container(height=500, border=True):
                    if genre_counts:
                        genre_df = pd.DataFrame(genre_counts.items(), columns=["Genre", "Count"])
                        fig = px.pie(genre_df, values="Count", names="Genre", title="Genre Distribution", hole=0.4)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error("🎧 No genre found.")
                    st.divider()

            with genre_col:
                st.markdown("#### 📊 Genre Counts")
                with st.container(height=500, border=True):
                    for genre, count in genre_counts.most_common():
                        st.markdown(f"- **{genre}**: {count}")
                    st.divider()

    if selected == "Playlists":
        analyzer = PlaylistAnalyzer(access_token)
        all_playlists = analyzer.get_all_playlists()

        if all_playlists:
            top_playlists = analyzer.get_top_playlists(all_playlists)

            if top_playlists:
                genres, playlist_summaries = analyzer.analyze_genres_from_playlists(top_playlists)
                genre_counts.update(genres)

                st.session_state.top_playlists = top_playlists
                st.session_state.genres = genres
                st.session_state.playlist_summaries = playlist_summaries
                st.session_state.genre_counts = genre_counts

                most_common_genre = genre_counts.most_common(1)[0][0]
                st.markdown(f"🎧 Founded Genre: **{most_common_genre}**")

            if not top_playlists:
                st.session_state.top_playlists = []
                st.session_state.genres = {}
                st.session_state.playlist_summaries = []
                st.session_state.genre_counts = Counter()

        main_col, chart_col, genre_col = st.columns([1, 1, 1])

        with main_col:
            st.markdown("### 🎼 Playlists")
            with st.container(height=500, border=True):
                if not all_playlists:
                    st.error("🎵 You don’t have any playlists to analyze.")
                else:
                    for playlist in playlist_summaries:
                        name = playlist["name"]
                        image = playlist["image"]
                        track_count = playlist["track_count"]

                        with st.container():
                            cols = st.columns([1, 3])
                            with cols[0]:
                                st.image(image, width=100)
                            with cols[1]:
                                st.markdown(f"### 📀 {name}")
                                st.markdown(f"🎵 **Number of Songs:** {track_count}")
                        st.divider()

        with chart_col:
            st.markdown("### 🍰 Genre Chart")
            with st.container(height=500, border=True):
                if genre_counts:
                    genre_df = pd.DataFrame(genre_counts.items(), columns=["Genre", "Count"])
                    fig = px.pie(genre_df, values="Count", names="Genre", title="Genre Distribution", hole=0.4)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error("🎧 No genre found.")
                st.divider()

        with genre_col:
            st.markdown("#### 📊 Genre Counts")
            with st.container(height=500, border=True):
                for genre, count in genre_counts.most_common():
                    st.markdown(f"- **{genre}**: {count}")
                st.divider()


# Sayfa ayarı
st.set_page_config(layout="wide")

# Sayfa başlığı
# st.title("🎵 Music to Movie")
# st.write("Hoş geldin! Spotify'daki müzik zevkine göre sana film önereceğiz.")

query_params = st.query_params
genre_counts = Counter()

if "access_token" not in st.session_state:
    st.session_state.access_token = None

if "queue_data" not in st.session_state:
    st.session_state.queue_data = None

if "code" in query_params and st.session_state.access_token is None:
    code = query_params["code"]
    token_response = get_access_token(code, redirect_uri=REDIRECT_URI)
    st.session_state.access_token = token_response.get("access_token")

# Token varsa
if st.session_state.access_token:
    access_token = st.session_state.access_token

    # Kullanıcı bilgilerini çek
    user_name = "Kullanıcı"
    user_image = None

    recommender = Recommender()

    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get("https://api.spotify.com/v1/me", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            user_name = user_data.get("display_name", "Kullanıcı")
            user_image = user_data.get("images", [{}])[0].get("url")
    except:
        pass

    # Sidebar tasarımı
    with st.sidebar:
        st.markdown(
            f"""
                    <div 
                        style="
                            text-align: center;
                            margin-left: 12px; 
                            margin-bottom: 50px; 
                            font-weight: bold;
                            font-size: 30px;
                    ">
                        🎵 Music to Movie
                    </div>
                    """,
            unsafe_allow_html=True
        )

        if user_image:
            st.markdown(
                f"""
                <div style="text-align: center;">
                    <img 
                        src="{user_image}" 
                        style="
                            width:150px; 
                            border-radius: 10px; 
                            margin-left: 10px;
                            margin-bottom: 15px;
                    ">
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown(
            f"""
            <div 
                style="
                    text-align: center;
                    margin-left: 12px; 
                    margin-bottom: 30px; 
                    font-weight: bold;
                    font-size: 24px;
            ">
                {user_name}
            </div>
            """,
            unsafe_allow_html=True
        )

        selected = option_menu(
            menu_title=None,
            options=["Home", "Analytics", "Settings"],
            icons=["house", "code-slash", "gear"],
            menu_icon="cast",
            default_index=0,
            orientation="vertical",
            styles={
                "container": {"background-color": "#1E1E1E", "padding": "10px"},
                "icon": {"color": "white", "font-size": "18px"},
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "5px",
                    "color": "white",
                    "background-color": "#83050B",
                },
                "nav-link-selected": {
                    "background-color": "#9B090E",
                    "font-weight": "bold",
                    "color": "white",
                },
            }
        )

        st.markdown("---")

        custom_css = """
        <style>
        div.stButton > button:first-child {
            background-color: #83050B;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: bold;
            width: 100%;
            text-align: center;
        }
        div.stButton > button:hover {
            background-color: #9B090E;
        }
        </style>
        """

        st.markdown(custom_css, unsafe_allow_html=True)

        if st.button("Refresh"):
            st.session_state.queue_data = get_user_queue(access_token)


    # Sayfa açıldığında ilk kez çekilecek veri
    if st.session_state.queue_data is None:
        st.session_state.queue_data = get_user_queue(access_token)

    queue_data = st.session_state.queue_data

    # Ana içerik aşağıda yazılacak.
    if selected == "Home":
        st.title("🎧 Home Page")
        st.write("Welcome to the movie recommendation system based on your Spotify music taste!")
        home_page(queue_data)

    elif selected == "Analytics":
        st.title("📊 Analytics")
        developer_mode(st.session_state.queue_data)

    elif selected == "Settings":
        st.title("⚙️ Settings")

        user_data = get_user_profile(st.session_state.access_token)

        if user_data:
            display_name = user_data.get("display_name", "Unknown")
            email = user_data.get("email", "Unknown")
            profile_pic = user_data["images"][0]["url"] if user_data.get("images") else None
            product = user_data.get("product", "Unknown").capitalize()
            country = user_data.get("country", "Unknown").capitalize()
            followers = user_data.get("followers", {}).get("total", 0)

            # --- Kullanıcı Kartı ---
            with st.container():
                st.subheader("👤 Spotify Profile")
                cols = st.columns([1, 3])
                with cols[0]:
                    if profile_pic:
                        st.image(profile_pic, use_container_width=True)
                    else:
                        st.info("No Profile Image.")
                with cols[1]:
                    st.markdown(f"**Name:** {display_name}")
                    st.markdown(f"**E-mail:** {email}")
                    st.markdown(f"**Product:** {product}")
                    st.markdown(f"**Country:** {country}")
                    st.markdown(f"**Followers:** {followers}")

            st.divider()

            # --- Veri Yönetimi (Butonlar hizalı) ---
            st.subheader("🔁 Data Management")

            if st.button("🧹 Clear Cache", key="clear"):
                st.cache_data.clear()
                st.success("Cache cleared!")

            if st.button("🔄 Reanalyze", key="reanalyze"):
                st.info("New analyze started...")
                st.session_state.queue_data = get_user_queue(access_token)

            if st.button("🔒Log out", help="logout", key="logout"):
                st.session_state.pop("access_token", None)
                st.session_state.clear()
                st.markdown(
                    f"""
                        <meta http-equiv="refresh" content="0; url={REDIRECT_URI}">
                        """,
                    unsafe_allow_html=True
                )

        else:
            st.error("❌ Spotify user information could not be retrieved. Please make sure you are logged in.")


else:
    st.markdown("""
        <style>
        .centered {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 80vh;
        }}
        .title {{
            font-size: 80px;
            font-weight: bold;
            margin-bottom: 120px;
            margin-top: -200px;
            color: white;
        }}
        .spotify-logo {{
            width: 300px;
            height: 300px;
            border-radius: 50%;
            box-shadow: 0 0 80px #1DB95488;
            transition: transform 0.3s;
        }}
        .spotify-logo:hover {{
            transform: scale(1.08);
            box-shadow: 0 0 500px #1DB954cc;
        }}

        </style>

        <div class="centered">
            <div class="title">Music to Movie</div>
            <a href="{0}">
                <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Spotify_logo_without_text.svg/2048px-Spotify_logo_without_text.svg.png" class="spotify-logo" />
            </a>
        </div>
    """.format(auth_url), unsafe_allow_html=True)

    login_messages = [
        "🎶 Let your music taste guide your next movie night. Log in to get cinematic.",
        "🎵 Every beat has a story. Let’s find the film that fits yours.",
        "🎧 Your vibes, your music, your movie match. Tap in with Spotify.",
        "🍿 Press play. We'll handle the movie magic.",
        "🎬 Turning your playlists into plot twists..."
    ]

    placeholder = st.empty()
    for i in range(100):
        message = login_messages[i % len(login_messages)]
        placeholder.markdown(f"<div style='text-align: center; font-size: 20px;'>{message}</div>",
                             unsafe_allow_html=True)
        time.sleep(5)
