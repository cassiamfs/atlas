generate_reviews_embeddings:
	python -c "from atlas_roots.functions import refresh_reviews_chroma_from_bigquery; refresh_reviews_chroma_from_bigquery()"
generate_places_embeddings:
	python -c "from atlas_roots.functions import refresh_chroma_from_bigquery; refresh_chroma_from_bigquery()"
generate_all_embeddings: generate_reviews_embeddings generate_places_embeddings



add:
	git add .
commit:
	gc -m "Test commit"
push:
	ggp
git_all: add commit push
