CREATE OR REPLACE VIEW $DATASET.movie_tags_view AS 
SELECT
    *
FROM $DATASET.movie_tags mt
WHERE tag NOT IN (SELECT tag FROM $DATASET.suppressed_tags);