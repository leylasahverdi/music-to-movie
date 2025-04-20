import streamlit as st
import pandas as pd
import joblib
import gdown
import pickle
import os

class Recommender:
    def __init__(self, model_path="DATA/emotion_score_model.pkl", data_path="DATA/movie_df_ml.csv"):
        self.get_model_from_data_folder()
        self.model = joblib.load(model_path)
        self.movie_df = pd.read_csv(
                            data_path,
                            encoding="ISO-8859-1",
                            on_bad_lines="skip"
                        )
        self.movie_df["emotion_score"] = pd.to_numeric(self.movie_df["emotion_score"], errors="coerce")
        self.X_columns = self.model.feature_names_in_

    @st.cache_resource
    def get_model_from_data_folder(_self=None):
        print("Downloading model")
        MODEL_URL = os.getenv("SPOTIFY_CLIENT_ID") or st.secrets.get("SPOTIFY_CLIENT_ID")
        output_path = os.path.join("DATA", "emotion_score_model.pkl")

        if not os.path.exists(output_path):
            print("Downloading model with gdown")
            gdown.download(MODEL_URL, output_path, quiet=False)

        with open(output_path, "rb") as f:
            print("Model loaded")
            model = pickle.load(f)

        return model

    def recommend_varied_films(self, genre_keyword, tolerance=3.0, top_n=3, candidate_pool=15):
        matched_cols = [col for col in self.X_columns if genre_keyword.lower() in col.lower()]

        if not matched_cols:
            pool = self.movie_df.sort_values(by="final_popularity", ascending=False).head(candidate_pool)
            sampled = pool.sample(n=min(top_n, len(pool)), random_state=None)
            return sampled[["title", "final_popularity", "vote_average", "genre_group"]]

        input_df = pd.DataFrame(data=[0]*len(self.X_columns), index=self.X_columns).T
        input_df.columns = self.X_columns
        for col in matched_cols:
            input_df.at[0, col] = 1

        try:
            predicted_score = self.model.predict(input_df)[0]
        except:
            pool = self.movie_df.sort_values(by="final_popularity", ascending=False).head(candidate_pool)
            sampled = pool.sample(n=min(top_n, len(pool)), random_state=None)
            return sampled[["title", "final_popularity", "vote_average", "genre_group"]]

        mask = self.movie_df["emotion_score"].between(predicted_score - tolerance, predicted_score + tolerance)
        filtered = self.movie_df[mask]

        if filtered.empty:
            pool = self.movie_df.sort_values(by="final_popularity", ascending=False).head(candidate_pool)
            sampled = pool.sample(n=min(top_n, len(pool)), random_state=None)
            return sampled[["title", "final_popularity", "vote_average", "genre_group"]]

        filtered_sorted = filtered.sort_values(by="final_score", ascending=False).head(candidate_pool)
        sampled = filtered_sorted.sample(n=min(top_n, len(filtered_sorted)), random_state=None)

        return sampled[["title", "emotion_score", "vote_average", "final_score", "genre_group"]]

