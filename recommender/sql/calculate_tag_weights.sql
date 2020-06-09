WITH tag_popularity AS (
  SELECT
    genome_tags.tag_id,
    LOG(COUNT(*)) as log_popularity
  FROM `movielens.genome_tags` genome_tags
  INNER JOIN `movielens.tags` tags 
  ON genome_tags.tag = tags.tag
  GROUP BY tag_id
),

tag_specificity AS (
  SELECT 
    tag_id,
    LOG(COUNT(*)) as log_specificity
  FROM `movielens.genome_scores`
  WHERE relevance > 0.5
  GROUP BY 1
)

SELECT
  tag_popularity.tag_id,
  log_popularity,
  log_specificity,
  log_popularity/log_specificity as tag_weight
FROM tag_popularity
INNER JOIN tag_specificity ON tag_popularity.tag_id = tag_specificity.tag_id
WHERE log_specificity > 0;