FROM python:3.12.11-slim-bookworm
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
COPY setup.py /atlas_roots/setup.py
COPY atlas_roots /atlas_roots
RUN pip install -e /atlas_roots
COPY db db/
CMD uvicorn atlas_roots.api.api:app --host 0.0.0.0 --port $PORT
