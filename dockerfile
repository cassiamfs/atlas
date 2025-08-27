FROM python:3.12.11-slim-bookworm
COPY  requirements.txt /requirements.txt
COPY atlas_roots /atlas_roots
COPY .env /atlas_roots/.env
COPY setup.py /atlas_roots/setup.py
RUN pip install -r /requirements.txt
CMD ["python", "/atlas_roots/main.py"]
