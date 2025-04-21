import streamlit as st
import requests
import os

OMDB_API_KEY = os.getenv("OMDB_API_KEY") or st.secrets.get("OMDB_API_KEY")

def get_poster_url_by_title(title):
    url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    response = requests.get(url)
    data = response.json()
    return data.get("Poster", None)
