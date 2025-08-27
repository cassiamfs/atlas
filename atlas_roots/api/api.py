
from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List
import requests
import os

from atlas_roots import data
from atlas_roots.functions import get_data, search_places_df


GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

app = FastAPI()

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
    # Use the search_places_df function to get predictions
    results = search_places_df(df, query, top_k)
    return {"predictions": results}

@app.get("/geocode/")
def geocode_address(address: str):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(url)
    return response.json()
