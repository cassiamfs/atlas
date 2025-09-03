import os
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
def predict_reviews(review: str, top_k: int = 5, type_of_places: str = None):

    results = search_reviews_with_chroma(review=review, top_k=top_k, type_of_places=type_of_places)

    return {"predictions": results}

@app.get('/search_all_in_one')
def search_all_in_one(
    city_query: str = "I want a quiet destination with lots of parks, and where I can enjoy good restaurant with music at night",
    seclusion: str="1,2,3",
    budget_level: str="1,2,3",
    region: str = None,
    top_k_places: int = 30,
    top_k_reviews: int = 5,
    restaurant_review: str = 'I want best italian food',
    museum_review: str = '',
    thing_to_do: str = '',
    park_review: str = ''

):

    types_of_places = ['restaurants', 'museum', 'things to do', 'parks']

    results = search_places_with_chroma(query=city_query, seclusion=seclusion, budget_level=budget_level, top_k=top_k_places, region=region).get('predictions')

    best_cities_names = [each.get("id") for each in results]

    user_queries = [restaurant_review,museum_review, thing_to_do, park_review ]

    review_results_object = {}

    for idx, each in enumerate(user_queries):
        if len(each) > 2:
            review_results = search_reviews_with_chroma(review = each, top_k=top_k_reviews, type_of_places=types_of_places[idx], cities=best_cities_names)
            review_results_object[types_of_places[idx]] = review_results

    return review_results_object
