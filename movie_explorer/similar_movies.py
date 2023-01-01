from collections import defaultdict
from typing import List, Dict
from google.cloud import bigquery
from jinja2 import Template

similar_movies_query_template = """
        WITH 
            {% if tags_to_boost or tags_to_penalise %}
            lhs_movie_tags AS (
              SELECT
                item_id,
                tag,
                CASE
                  {% if tags_to_boost %} WHEN tag IN UNNEST(@tags_to_boost) THEN 0.9 {% endif %} 
                  {% if tags_to_penalise %} WHEN tag IN UNNEST(@tags_to_penalise) THEN 0.1 {% endif %} 
                  ELSE score
                END as score
              FROM `movielens.movie_tags`
              WHERE item_id IN UNNEST(@movie_ids)
            ),
            lhs_unit_scores AS (
              SELECT
                item_id,
                tag,
                score,
                score/SQRT(SUM(POW(score, 2)) OVER (PARTITION BY item_id)) as unit_score
              FROM lhs_movie_tags
            ),            
            {% else %}
            lhs_unit_scores AS (
              SELECT
                item_id,
                tag,
                unit_score
              FROM `movielens.movie_tags_unit_score`
              WHERE item_id IN UNNEST(@movie_ids)
            ),
            {% endif %}
            similarities AS (
              SELECT
                lhs.item_id as reference_movie_id,
                rhs.item_id as comparison_movie_id,
                SUM(lhs.unit_score * rhs.unit_score) as similarity_score
              FROM lhs_unit_scores lhs
              INNER JOIN `movielens.movie_tags_unit_score` rhs ON lhs.tag = rhs.tag
              WHERE lhs.item_id <> rhs.item_id
              GROUP BY 1, 2
            ),            
            ranked_similarities AS (
            SELECT
              movies.item_id as movie_id,
              similarities.reference_movie_id,
              similarities.similarity_score,
              ROW_NUMBER() OVER (PARTITION BY similarities.reference_movie_id ORDER BY similarities.similarity_score DESC) as similarity_rank
            FROM `movielens.movies` movies
            INNER JOIN similarities ON movies.item_id = similarities.comparison_movie_id
            )        
            SELECT 
              * 
            FROM ranked_similarities 
            WHERE similarity_rank <= @results_per_movie
    """


def get_similar(movie_ids: List[int],
                number_of_results: int = 10,
                tags_to_boost: List[str] = None,
                tags_to_penalise: List[str] = None) -> Dict[int, Dict[int, float]]:
    """
    Finds the most similar movies to the provided list of movie ids using Cosine Similarity.

    If a movie id does not exist it is not included in the results
    :param movie_ids:
    :type movie_ids:
    :param number_of_results:
    :type number_of_results:
    :return:
    :rtype:
    """
    bq_client = bigquery.Client()

    job_config = bigquery.job.QueryJobConfig()
    query_parameters = [
        bigquery.ArrayQueryParameter("movie_ids", "INT64", movie_ids),
        bigquery.ScalarQueryParameter(
            "results_per_movie", "INT64", number_of_results)
    ]

    if tags_to_boost:
      query_parameters.append(bigquery.ArrayQueryParameter("tags_to_boost", "STRING", tags_to_boost))

    if tags_to_penalise:
      query_parameters.append(bigquery.ArrayQueryParameter("tags_to_penalise", "STRING", tags_to_penalise))

    job_config.query_parameters = query_parameters
    print(job_config.query_parameters)

    query = Template(similar_movies_query_template).render(tags_to_boost=tags_to_boost, tags_to_penalise=tags_to_penalise)
    results = bq_client.query(query, job_config)
    similar_movies = defaultdict(dict)

    for row in results:
        similar_movies[row["reference_movie_id"]
                       ][row["movie_id"]] = row["similarity_score"]

    return similar_movies
