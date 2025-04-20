# spotify_api.py
import streamlit as st
import requests


def get_user_queue(access_token):
    url = "https://api.spotify.com/v1/me/player/queue"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.status_code, "message": response.text}

@st.cache_data(show_spinner=False)
def get_artist_genres(artist_id, access_token):
    url = f"https://api.spotify.com/v1/artists/{artist_id}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    res = requests.get(url, headers=headers)
    print("SPOTIFY GET ARTIST ENDPOINT STATUS CODE: " + str(res.status_code))
    if res.status_code == 200:
        return res.json().get("genres", [])
    else:
        return []

@st.cache_data(show_spinner=False)
def get_user_profile(access_token):
    url = "https://api.spotify.com/v1/me"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return res.json()
    else:
        print(f"Spotify user fetch error: {res.status_code} - {res.text}")
        return None