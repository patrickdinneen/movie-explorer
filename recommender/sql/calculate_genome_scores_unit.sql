SELECT
  item_id,
  tag,
  score,
  score/SQRT(SUM(POW(score, 2)) OVER (PARTITION BY item_id)) as unit_score
FROM `$DATASET.movie_tags_view`
