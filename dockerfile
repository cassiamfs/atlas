FROM python:3.12.11-slim-bookworm
COPY  requirements.txt /requirements.txt
COPY atlas_roots /atlas_roots
COPY setup.py /atlas_roots/setup.py
RUN pip install -r /requirements.txt
RUN pip install .
CMD uvicorn atlas_roots.api.api:app --host 0.0.0.0 --port $PORT 
