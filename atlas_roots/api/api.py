import os
import requests
import chromadb
from sentence_transformers import SentenceTransformer
from fastapi import FastAPI
from atlas_roots.functions import  search_places_with_chroma, search_reviews_with_chroma



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
def predict_reviews(review, k_neighbors=5):

    """
    Predicts the top_k reviews from the dataset that match the user's query.
    """

    # Use the search_places_df function to get predictions
    results = search_reviews_with_chroma(review=review, k_neighbors=k_neighbors)

    return {"predictions": results}


    """
    Geocode an address using the Google Maps API.
    """

    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_MAPS_API_KEY}"

    response = requests.get(url)
    data = response.json()
    if data.get("status") == "OK":
        result = data["results"][0]
        location = result['geometry']['location']
        return {
            "formatted_address": result["formatted_address"],
            "latitude": result["geometry"]["location"]["lat"],
            "longitude": result["geometry"]["location"]["lng"]
        }
    else:
        return {"error": "Unable to geocode the address.", "details": data}
