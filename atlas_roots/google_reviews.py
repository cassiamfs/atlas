from google.cloud import bigquery
import pandas as pd
import os

#from googlemaps.places import places
from atlas_roots.api.load import load_data
import googlemaps
API_KEY = os.environ["API_KEY"]
gmaps = googlemaps.Client(key=API_KEY)

import tqdm


def get_reviews():
    """This function creates a DataFrame containing
    [city, type_of_place, name, rating, address and review] from Google Places API."""

    query = "SELECT city FROM `velvety-being-470310-a3.atlas.cities`"

    cities_bq = load_data(query)

    # Gets a list of cities from 'cities' table in BigQuery
    cities = cities_bq['city'].tolist()
    # Defines keywords for the types of places we want reviews of
    types_of_places = ['restaurants', 'museum', 'things to do', 'parks']

    # Loops through each city with a progress bar
    data = []
    for city in tqdm.tqdm(cities):
        # Loops through each type of place for the current city
        for type_of_place in types_of_places:
            # Uses Google Places API to search for places matching the query (type in city)
            results = places(client=gmaps, query=f"{type_of_place} in {city}").get('results')
            for place in results:
                # Extracts the unique place ID
                place_id = place.get('place_id')
                # Fetchs detailed information about the place using the place ID
                place_info = gmaps.place(place_id)
                if "reviews" in place_info['result'].keys():
                    place_review=place_info.get('reviews')
                    for specific_place in place_info.get('result').get('reviews'):
                        if "text" in specific_place.keys():
                            review = specific_place.get("text")
                            name = place_info['result']['name']
                            address = place_info['result'].get('formatted_address', 'no adress')
                            rating = place_info['result'].get('rating', 'no rating')
                            # Stores the extracted information in a dictionary and append it to the data list
                            data.append({"city":city,
                                        "type_of_place":type_of_place,
                                        "name": name,
                                        "rating": rating,
                                        "address": address,
                                        "review": review,})
    df = pd.DataFrame(data)

    return df

def load_data_to_bq(df):
    """This function loads the DataFrame onto BigQuery"""
    # Get the GCP project ID and BigQuery dataset name from .env variables
    # Define the target table name as 'reviews'
    PROJECT = os.environ['GCP_PROJECT']
    DATASET = os.environ['BQ_DATASET']
    TABLE = 'reviews'

    table = f"{PROJECT}.{DATASET}.{TABLE}"

    client = bigquery.Client()
    # Actually loads the new table to BQ or append in case we are generating the DF in multiple steps
    write_mode = "WRITE_TRUNCATE" # or "WRITE_APPEND"
    job_config = bigquery.LoadJobConfig(write_disposition=write_mode)

    job = client.load_table_from_dataframe(df, table, job_config=job_config)
    result = job.result()


# def get_data():
#     return data

# def upload_data(data) -> None:
#     upload_data(data)

def main():
    # Calls 'get_reviews' function to collect data
    data = get_reviews()
    # Passes the collected data to the function that uploads it to BigQuery
    load_data_to_bq(data)

# main() is only ran when executed directly (not when imported as a module)
if __name__ == '__main__':
    main()
