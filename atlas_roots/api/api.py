from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {'greeting': 'Hello'}


@app.get('/search')
def search(query: str):
    return {'search_query': query}

@app.get('/predict')
def predict(data: dict):
    return {'prediction': data}

