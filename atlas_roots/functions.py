from sentence_transformers import SentenceTransformer, util
from typing import List
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from atlas_roots.api.load import load_data, PROJECT,DATASET, TABLE

def search_places_df(df, query, top_k: int = 3):
    """
    Search for places from a DataFrame that match the user's continent, features, and season preferences.
    """

    #Load data
    model = SentenceTransformer("sentence-transformers/multi-qa-mpnet-base-dot-v1")
    query_emb = model.encode(query, convert_to_tensor=True)



    # 2. User questioning

    # 3. Filter description from dataframe
    descriptions = df['short_description'].tolist()
    embeddings = model.encode(descriptions, convert_to_tensor=True)

    # 4. Calculate cosine similarity
    cos_scores = util.cos_sim(query_emb, embeddings)[0]

    # 5. Top K results
    top_indices = cos_scores.argsort(descending=True)[:top_k]


    # 6. Results
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



def get_data() -> pd.DataFrame:
    """
    Open data from csv.
    """

    query = f"""
    SELECT *
    FROM {PROJECT}.{DATASET}.{TABLE}
    """
    df = load_data(query)

    # This section has to be according to the dataframe structure
    df = df[['city', 'country', 'short_description', 'region', 'latitude and longitude']]

    return df


if __name__ == "__main__":
    # Example usage
    df = get_data()
    results = search_places_df(df,  "i want quiet town near the sea")
    for r in results:
        print(f"City: {r['id']} Country:{r['name']} ({r['score']:.2f}): {r['description']}")
