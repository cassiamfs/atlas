from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import chromadb
from atlas_roots.api.load import load_data, PROJECT, DATASET, TABLE
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
    features_df = df.drop(['short_description'], axis=1)
    unique_ids = [f"{city}_{i}" for i, city in enumerate(df['city'])]


    collection.add(
            ids=unique_ids,
            documents=list(df["short_description"]),
            metadatas=features_df.to_dict(orient="records"),
            embeddings=list(embeddings)
        )



def store_embeddings_reviews(df):
    """
    Generate embeddings for reviews and store them in Chroma.
    """
    collection = client.create_collection("reviews_embeddings")

    reviews = df['review'].tolist()
    embeddings = model.encode(reviews)

    # Save embeddings in Chroma
    features_df = df.drop(['review'], axis=1)
    unique_ids = [f"review_{i}" for i in range(len(reviews))]

    collection.add(
        ids=unique_ids,
        documents=list(df["review"]),
        metadatas=features_df.to_dict(orient="records"),
        embeddings=list(embeddings)
    )

def search_reviews_with_chroma(review, k_neighbors=5):
    """
    Compare new reviews with existing place descriptions' embeddings.

    new_reviews: List of new reviews that need to be compared.
    KNN: Number of closest places to consider for each new review.
    """
    new_review_embeddings = model.encode(review)  # Generating embeddings for new reviews

    collection = client.get_collection("reviews_embeddings") #New collection
    existing_embeddings = collection.get_collection('places_embeddings')  # Embeddings of place descriptions
    existing_place_ids = collection.get_ids()  # Place IDs (so you can identify which place the embedding belongs to)

    similarities = cosine_similarity(new_review_embeddings, existing_embeddings)

    # For each new review, find the K closest places based on cosine similarity
    top_k_similarities = np.argsort(similarities, axis=1)[:, -k_neighbors:]

    updated_clusters = []  # To store the results of the new reviews' similarity analysis

    # For each new review, determine the most similar places
    for i, new_review in enumerate(review):
        # Get the indices of the most similar places
        similar_indices = top_k_similarities[i]
        # Get the place IDs for the most similar places
        similar_places = [existing_place_ids[idx] for idx in similar_indices]
        # Get the corresponding similarity scores for these places
        similar_similarities = [similarities[i][idx] for idx in similar_indices]

        updated_clusters.append({
            "new_review": new_review,
            "similar_places": similar_places,
            "similar_similarities": similar_similarities
        })

    return updated_clusters

def search_places_with_chroma(query: str,seclusion, top_k: int = 5, region: str = None):
    """
    Search in ChromaDB using embeddings and return results with metadata.
    """
    query_embedding = model.encode(query).tolist()
    collection = client.get_collection(name="places_embeddings")

    filters = {}
    predictions =  []

    if region:
        filters.update({"region":region})

    if seclusion:
        filters.update({"seclusion":seclusion})

    if len(filters.keys()) > 0:
        # Add logical and operator for filters
        filters = {"$and": [{key: value} for key, value in filters.items()]}

    if len(filters.keys()) > 0:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filters
        )
    else:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

    for doc, meta, id, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["ids"][0],
        results["distances"][0]
    ):
        lat, lon = None, None
        if meta.get("latitude and longitude"):
            lat, lon = map(float, meta["latitude and longitude"].split(","))



        predictions.append({
            "id": meta.get('city'),
            'country': meta.get('country'),
            'region': meta.get('region'),
            'seclusion': meta.get('seclusion'),
            "cluster": meta.get('cluster'),
            "description": doc,
            "score": float(distance),
            "latitude": lat,
            "longitude": lon,

        })

    #reranked = rerank_with_metadata(places_info, user_profile, alpha)

    return {"predictions": predictions}

def refresh_chroma_from_bigquery():
    """
    Load data from BigQuery and store embeddings in Chroma.
    """

    query = f"SELECT * FROM {PROJECT}.{DATASET}.{TABLE}"
    df = load_data(query)


    collection_names = [name.name for name in client.list_collections()]
    if "places_embeddings" in collection_names:
        client.delete_collection("places_embeddings")

    store_embeddings_in_chroma(df)

    return {"status": "Chroma updated", "rows": len(df)}

def refresh_reviews_chroma_from_bigquery():
    """
    Load data from BigQuery and store embeddings in Chroma.
    """
    dataset = os.environ["BQ_DATASET"]
    table = "reviews"

    query = f"SELECT * FROM `{PROJECT}.{DATASET}.{table}`"
    df = load_data(query)

    collection_names = [name.name for name in client.list_collections()]
    if "reviews_embeddings" in collection_names:
        client.delete_collection("reviews_embeddings")

    store_embeddings_reviews(df)

    return {"status": "Chroma updated", "rows": len(df)}


if __name__ == "__main__":
    result = refresh_chroma_from_bigquery()
    print(result)

    #result = search_places_with_chroma(query='small town in italy with museums and wine', seclusion=3, top_k=3, region="Europe")
    #print(result)



    #query = "SELECT * FROM velvety-being-470310-a3.atlas.cities"
    #df = load_data(query)
