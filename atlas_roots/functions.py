from sentence_transformers import SentenceTransformer, util
from typing import List
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import chromadb
from chromadb.config import Settings

client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory="path to directory"))
model = SentenceTransformer("sentence-transformers/multi-qa-mpnet-base-dot-v1")
client = chromadb.Client()
collection = client.create_collection("places_embeddings")

def get_data(file_path: str) -> pd.DataFrame:
    """
    Open data from csv.
    """
    # Load the DataFrame from a CSV file (you can change this if you use another source)
    df = pd.read_csv(file_path)

    # This section has to be according to the dataframe structure
    df = df[['city', 'country', 'short_description', 'region']]

    return df

def store_embeddings_in_chroma(df):
    """
    Store embeddings in Chroma.
    """
    descriptions = df['short_description'].tolist()
    embeddings = model.encode(descriptions)

    # Save embaddings in chroma
    for i, embedding in enumerate(embeddings):
        collection.add(
            documents=[df.iloc[i]["short_description"]],
            metadatas=[{"city": df.iloc[i]["city"], "country": df.iloc[i]["country"]}],
            embeddings=[embedding]
        )

def search_places_with_chroma(query: str, top_k: int = 3):
    """
    Search for places in ChromaDB that match the user's query.
    """
    query_embedding = model.encode(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    predictions = []
    for result in results['documents']:
        predictions.append({
            "city": result['metadata']['city'],
            "country": result['metadata']['country'],
            "description": result['documents'][0],
            "score": result['score']
        })

    return predictions

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
        results.append({
            "id": row["city"],
            "name": row["country"],
            "description": row["short_description"],
            "score": float(cos_scores[idx])
        })

    return results



if __name__ == "__main__":
    # Example usage
    df = get_data("/home/scofeels/code/cassiamfs/atlas/.csv/filtered_cities_final.csv")

    if len(collection.get()) == 0:
        store_embeddings_in_chroma(df)  #This helps to save embeddings if the didnt previously

    results = search_places_df(df,  "i want quiet town near the sea")
    for r in results:
        print(f"City: {r['id']} Country:{r['name']} ({r['score']:.2f}): {r['description']}")
