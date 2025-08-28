from sentence_transformers import SentenceTransformer, util
from typing import List
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import chromadb
from chromadb.config import Settings
from chromadb import EmbeddingFunction



client = chromadb.PersistentClient(path='db')
model = SentenceTransformer("sentence-transformers/multi-qa-mpnet-base-dot-v1")

def get_data(file_path: str) -> pd.DataFrame:
    """
    Open data from csv.
    """
    # Load the DataFrame from a CSV file (you can change this if you use another source)
    df = pd.read_csv(file_path)


    # This section has to be according to the dataframe structure
    df = df[['city', 'country', 'short_description', 'region', 'latitude and longitude']]

    return df


def store_embeddings_in_chroma(df):
    """
    Store embeddings in Chroma.
    """

    collection = client.create_collection("places_embeddings")

    descriptions = df['short_description'].tolist()
    embeddings = model.encode(descriptions)

    # Save embaddings in chroma
    features_df = df.drop(['short_description','city'], axis=1)

    collection.add(
            ids=list(df['city']),
            documents=list(df["short_description"]),
            metadatas=features_df.to_dict(orient="records"),
            embeddings=list(embeddings)
        )

def search_places_with_chroma(query: str, top_k: int = 3):
    """
    Search for places in ChromaDB that match the user's query and return relevant information.
    """
    query_embedding = model.encode(query)
    collection = client.get_collection(name="places_embeddings")

# Perform the query to get the top_k results
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k  #filters
    )

# Extract relevant information from the query results
    places_info = []
    for idx, doc in enumerate(results['documents']):
        # Metada updated, but need changes with bigquery
        metadata = results['metadatas'][idx]

        if isinstance(metadata, list):
            metadata = metadata[0]

        city = metadata.get("city", "Unknown City")
        country = metadata.get("country", "Unknown Country")
        lat_lon_str = metadata.get("latitude and longitude", "0,0")
        latitude, longitude = map(float, lat_lon_str.split(','))

# Combine the info into a dictionary
        place_data = {
            "id": city,  # This should be changed into id later with BigQuery
            "name": country,
            "description": doc,  # the document which contains the short description
            "score": results['distances'][idx],  # Distance/score from the query embedding
            "latitude": latitude,
            "longitude": longitude
        }
        places_info.append(place_data)

    return places_info


def search_places_df(df, query, top_k: int = 3):
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
    # Example usage
    df = get_data("atlas_roots/.csv/filtered_cities_final.csv")

    store_embeddings_in_chroma(df)  #This helps to save embeddings if the didnt previously
    result = search_places_with_chroma(query='small town in italy with museums and wine', top_k=3)
    print(result)

    #results = search_places_df(df,  "i want quiet town near the sea")
    #for r in results:
        #print(f"City: {r['id']} Country:{r['name']} ({r['score']:.2f}): {r['description']}")
