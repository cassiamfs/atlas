from google.cloud import bigquery
import os

PROJECT = os.environ['GCP_PROJECT']
DATASET = os.environ['BQ_DATASET']
TABLE = os.environ['BQ_TABLE']

query = f"""
    SELECT *
    FROM {PROJECT}.{DATASET}.{TABLE}
    """


def load_data():
    client = bigquery.Client(project=PROJECT)
    query_job = client.query(query)
    result = query_job.result()
    df = result.to_dataframe()

    return df


if __name__ == "__main__":
    print(load_data().head())
