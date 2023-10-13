WITH ranked_tags AS (
  SELECT
    *,
    ROW_NUMBER() OVER (PARTITION BY item_id ORDER BY score DESC) as tag_rank
  FROM `$DATASET.movie_tags_view`
),
top_n_tags AS (
  SELECT 
    * 
  FROM ranked_tags 
  WHERE tag_rank < 41
)
SELECT
  item_id,
  tag,
  score,
  score/SQRT(SUM(POW(score, 2)) OVER (PARTITION BY item_id)) as unit_score
FROM top_n_tags
