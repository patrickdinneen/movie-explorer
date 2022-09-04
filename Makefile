import_data:
	bq load --autodetect --source_format=NEWLINE_DELIMITED_JSON $(DATASET).movies data/movie_dataset_public_final/raw/metadata_updated.json
	bq load --autodetect --source_format=NEWLINE_DELIMITED_JSON $(DATASET).tags data/movie_dataset_public_final/raw/tags.json
	bq load --autodetect --source_format=CSV $(DATASET).movie_tags data/movie_dataset_public_final/scores/tagdl.csv

create_unit_vectors:
	cat recommender/sql/calculate_genome_scores_unit.sql | envsubst | bq query --use_legacy_sql=false --replace=true --destination_table=$(DATASET).movie_tags_unit_score