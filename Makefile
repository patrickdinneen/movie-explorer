DATASET=movielens

import_data:
	bq load --autodetect --source_format=CSV --replace --schema=tag $(DATASET).suppressed_tags data/suppressed_tags.csv
	# bq load --autodetect --source_format=NEWLINE_DELIMITED_JSON --replace $(DATASET).movies data/metadata_updated.json.gz
	# bq load --autodetect --source_format=NEWLINE_DELIMITED_JSON --replace $(DATASET).tags data/tags.json.gz
	# bq load --autodetect --source_format=CSV --replace $(DATASET).movie_tags data/tag_scores.csv.gz

create_unit_vectors:
	cat recommender/sql/movie_tags_view.sql | envsubst | bq query --use_legacy_sql=false
	cat recommender/sql/calculate_genome_scores_unit.sql | envsubst | bq query --use_legacy_sql=false --replace=true --destination_table=$(DATASET).movie_tags_unit_score
	cat recommender/sql/calculate_genome_scores_unit_truncated.sql | envsubst | bq query --use_legacy_sql=false --replace=true --destination_table=$(DATASET).movie_tags_unit_score_truncated
