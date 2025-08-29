from google.cloud import bigquery
import os

PROJECT = os.environ['GCP_PROJECT']
DATASET = os.environ['BQ_DATASET']
TABLE = os.environ['BQ_TABLE']



def load_data(query):
    client = bigquery.Client(project=PROJECT)
    query_job = client.query(query)
    result = query_job.result()
    df = result.to_dataframe()

    return df


if __name__ == "__main__":
    query = f"""
    SELECT *
    FROM {PROJECT}.{DATASET}.{TABLE}
    """

    print(load_data(query).head())
