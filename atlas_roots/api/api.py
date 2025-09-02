import os
import requests
import chromadb
from sentence_transformers import SentenceTransformer
from fastapi import FastAPI
from atlas_roots.functions import  search_places_with_chroma, search_reviews_with_chroma, search_combined_with_chroma



GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

app = FastAPI()

client = chromadb.Client()
collection = client.create_collection("places_embeddings")

model = SentenceTransformer("sentence-transformers/multi-qa-mpnet-base-dot-v1")


@app.get("/")
def root():
    return {'message': 'Welcome to AtlasRoot API'}

@app.get('/predict_city')
def predict_city(query:str, seclusion:int=None, top_k: int=30, region:str=None ):

    """
    Predicts the top_k cities from the dataset that match the user's query.
    """

    # Use the search_places_df function to get predictions
    results = search_places_with_chroma(query=query,
        seclusion=seclusion,
        top_k=top_k,
        region=region)

    return {"predictions": results}

@app.get('/predict_reviews')
def predict_reviews(review: str, top_k: int = 5, type_of_places: str = None):

    """
    Predicts the top_k reviews from the dataset that match the user's query.
    """

    # Use the search_places_df function to get predictions
    results = search_reviews_with_chroma(review=review, top_k=top_k, type_of_places=type_of_places)

    return {"predictions": results}

@app.get("/predict_combined")
def predict_combined(
    query: str,
    top_k_cities: int = 5,
    top_k_places: int = 3,
    top_k_reviews: int = 3,
    seclusion: int = None,
    region: str = None,
    type_of_places: str = None
):
    """
    For each top city, return up to 3 places with their reviews.
    """
    results = search_combined_with_chroma(
        query=query,
        top_k_cities=top_k_cities,
        top_k_places=top_k_places,
        top_k_reviews=top_k_reviews,
        seclusion=seclusion,
        region=region,
        type_of_places=type_of_places
    )
    return results
