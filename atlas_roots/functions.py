from sentence_transformers import SentenceTransformer, util
from typing import List
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def search_places_df(df, query, top_k: int = 3, selected_regions: List[str] = None):
    """
    Search for places from a DataFrame that match the user's continent, features, and season preferences.
    """
    model = SentenceTransformer("sentence-transformers/multi-qa-mpnet-base-dot-v1")
    query_emb = model.encode(query, convert_to_tensor=True)

    # Filter by selected regions if provided
    if selected_regions:
        df = df[df['region'].isin(selected_regions)]

    descriptions = df['short_description'].tolist()
    embeddings = model.encode(descriptions, convert_to_tensor=True)

    cos_scores = util.cos_sim(query_emb, embeddings)[0]
    top_indices = cos_scores.argsort(descending=True)[:top_k]

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

def get_data(file_path: str) -> pd.DataFrame:
    """
    Open data from csv.
    """
    # Load the DataFrame from a CSV file (you can change this if you use another source)
    df = pd.read_csv(file_path)

    # This section has to be according to the dataframe structure
    df = df[['city', 'country', 'short_description', 'region', 'latitude and longitude']]

    return df

if __name__ == "__main__":
    # Example usage
    df = get_data("/home/scofeels/code/cassiamfs/atlas/.csv/filtered_cities_final.csv")
    results = search_places_df(df,  "i want quiet town near the sea")
    for r in results:
        print(f"City: {r['id']} Country:{r['name']} ({r['score']:.2f}): {r['description']}")
