import os
import requests
import chromadb
from sentence_transformers import SentenceTransformer
from fastapi import FastAPI
from typing import List
from pydantic import BaseModel
from atlas_roots import data
from atlas_roots.functions import get_data, search_places_df, store_embeddings_in_chroma



GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

app = FastAPI()

client = chromadb.Client()
collection = client.create_collection("places_embeddings")

model = SentenceTransformer("sentence-transformers/multi-qa-mpnet-base-dot-v1")


@app.get("/")
def root():
    return {'greeting': 'Hello'}


@app.get('/search')
def search(query: str):
    return {'search_query': query}


@app.get('/predict_city')
def predict_city(query:str, top_k: int = 3):
    # Load the cities data from CSV
    df = get_data("atlas_roots/.csv/filtered_cities_final.csv")
    # Embed the city names
    if len(collection.get()) == 0:
        store_embeddings_in_chroma(df)
    # Use the search_places_df function to get predictions
    results = search_places_df(df, query, top_k)
    return {"predictions": results}

@app.get("/geocode/")
def geocode_address(address: str):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(url)
    return response.json()
