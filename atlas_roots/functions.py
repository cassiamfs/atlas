from sentence_transformers import SentenceTransformer, util
from typing import List
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import chromadb
from chromadb.config import Settings
from chromadb import EmbeddingFunction
from atlas_roots.api.load import load_data
import os


client = chromadb.PersistentClient(path='db')
model = SentenceTransformer("sentence-transformers/multi-qa-mpnet-base-dot-v1")

def store_embeddings_in_chroma(df):
    """
    Store embeddings in Chroma.
    """

    collection = client.create_collection("places_embeddings")

    descriptions = df['short_description'].tolist()
    embeddings = model.encode(descriptions)

# Save embaddings in chroma
    features_df = df.drop(['short_description','city'], axis=1)
    unique_ids = [f"{city}_{i}" for i, city in enumerate(df['city'])]


    collection.add(
            ids=unique_ids,
            documents=list(df["short_description"]),
            metadatas=features_df.to_dict(orient="records"),
            embeddings=list(embeddings)
        )

def search_places_with_chroma(query: str, top_k: int = 3, region: str = None):
    """
    Search in ChromaDB using embeddings and return results with metadata.
    """
    query_embedding = model.encode(query).tolist()
    collection = client.get_collection(name="places_embeddings")

    filters = {"region": region} if region else None
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=filters
    )

    places_info = []
    for doc, meta, id, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["ids"][0],
        results["distances"][0]
    ):
        lat, lon = None, None
        if meta.get("latitude and longitude"):
            lat, lon = map(float, meta["latitude and longitude"].split(","))

        places_info.append({
            "id": id,
            "name": meta.get("country"),
            "description": doc,
            "score": float(distance),
            "latitude": lat,
            "longitude": lon
        })

    return places_info

def refresh_chroma_from_bigquery():
    """
    Load data from BigQuery and store embeddings in Chroma.
    """
    dataset = os.environ["BQ_DATASET"]
    table = os.environ["BQ_TABLE"]

    query = f"SELECT * FROM `{dataset}.{table}`"
    df = load_data(query)

    if "places_embeddings" in client.list_collections():
        client.delete_collection("places_embeddings")

    store_embeddings_in_chroma(df)

    return {"status": "Chroma updated", "rows": len(df)}


#def search_places_df(df, query, top_k: int = 3):
    """
    Search for places from a DataFrame that match the user's continent, features, and season preferences.
    """
    query_emb = model.encode(query, convert_to_tensor=True)

    descriptions = df['short_description'].tolist()
    embeddings = model.encode(descriptions, convert_to_tensor=True)
    cos_scores = util.cos_sim(query_emb, embeddings)[0]
    top_indices = cos_scores.argsort(descending=True)[:top_k]

# Results
    results = []
    for idx in top_indices:
        row = df.iloc[int(idx)]
        lat_lon_str = row["latitude and longitude"]
        lat, lon = map(float, lat_lon_str.split(','))
        results.append({
            "id": row["city"],
            "name": row["country"],
            "description": row["short_description"],
            "score": float(cos_scores[idx]),
            "latitude": lat,
            "longitude": lon
        })

    return results



if __name__ == "__main__":

    result = search_places_with_chroma(query='small town in italy with museums and wine', top_k=3, region='Europe')
    print(result)



    #query = "SELECT * FROM velvety-being-470310-a3.atlas.cities"
    #df = load_data(query)
    #store_embeddings_in_chroma(df)
    #print("Chroma updated with data from BigQuery")
