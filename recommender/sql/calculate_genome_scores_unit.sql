SELECT
  movie_id,
  tag_id,
  relevance,
  relevance/SQRT(SUM(POW(relevance, 2)) OVER (PARTITION BY movie_id)) as unit_relevance
FROM `movielens.genome_scores`