import duckdb
import pandas as pd

from functools import cache
from typing import List, Dict, Optional, Set

from jinja2 import Template

from movie_explorer.model import Movie

lhs_unit_scores_cte_template = """
          {% if tags_to_boost or tags_to_drop %}
            lhs_movie_tags AS (
              SELECT
                item_id,
                tag,
                CASE
                  {% if tags_to_boost %} WHEN tag IN ({% for tag_to_boost in tags_to_boost %}
                    $tag_to_boost_{{ loop.index0 }}{% if not loop.last %},{% endif %}{% endfor %}
                  ) THEN 0.9 {% endif %} 
                  ELSE score
                END as score
              FROM 'data/movie_tags.parquet'
              WHERE item_id = $lhs_id
              {% if tags_to_drop %} AND tag NOT IN ({% for t in tags_to_drop %}
                $tag_to_drop_{{ loop.index0 }}{% if not loop.last %},{% endif %}{% endfor %}
              ){% endif %} 
              {% if tags_to_boost %}
              UNION DISTINCT
              {% for tag in tags_to_boost %}
              SELECT
                {{ movie_id }} as item_id,
                '{{ tag }}' as tag,
                0.9 as score
              {% if not loop.last %}
              UNION DISTINCT
              {% endif %}
              {% endfor %}
              {% endif %}
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
                score,
                unit_score
              FROM 'data/movie_tags.parquet'
              WHERE item_id = $lhs_id
            ){% endif %}
"""

similar_movies_query_template = """
        WITH 
            {{ lhs_unit_scores_cte }},
            similarities AS (
              SELECT
                lhs.item_id as reference_movie_id,
                rhs.item_id as comparison_movie_id,
                SUM(lhs.unit_score * rhs.unit_score) as similarity_score
              FROM lhs_unit_scores lhs
              INNER JOIN 'data/movie_tags.parquet' rhs ON lhs.tag = rhs.tag
              WHERE lhs.item_id <> rhs.item_id
              GROUP BY 1, 2
            ),            
            ranked_similarities AS (
            SELECT
              movies.item_id as movie_id,
              movies.title,
              movies.imdb_id,
              similarities.similarity_score,
              ROW_NUMBER() OVER (PARTITION BY similarities.reference_movie_id ORDER BY similarities.similarity_score DESC) as similarity_rank
            FROM 'data/movies.parquet' movies
            INNER JOIN similarities ON movies.item_id = similarities.comparison_movie_id
            )        
            SELECT 
              * 
            FROM ranked_similarities 
            WHERE similarity_rank <= $number_of_results
    """

explain_similarity_query = """
        WITH 
          {{ lhs_unit_scores_cte }}
          SELECT
            rhs.tag,
            lhs.score as lhs_tag_score,
            rhs.score as rhs_tag_score,
            lhs.unit_score * rhs.unit_score * 100 as tag_percentage
          FROM 'data/movie_tags.parquet' rhs
          LEFT JOIN lhs_unit_scores lhs ON lhs.tag = rhs.tag
          LEFT JOIN 'data/movies.parquet' lhs_movie ON lhs.item_id = lhs_movie.item_id 
          LEFT JOIN 'data/movies.parquet' rhs_movie ON rhs.item_id = rhs_movie.item_id 
          WHERE rhs.item_id = $rhs_id              
          ORDER BY tag_percentage DESC
    """


def _get_lhs_unit_scores_cte(movie_id: int,
                             tags_to_boost: Optional[List[str]], 
                             tags_to_drop: Optional[List[str]]) -> str:
   return Template(lhs_unit_scores_cte_template).render(movie_id=movie_id,
                                                        tags_to_boost=tags_to_boost,
                                                        tags_to_drop=tags_to_drop)


@cache
def get_similar(movie_id: int,
                number_of_results: int = 10,
                tags_to_boost: Optional[List[str]] = None,
                tags_to_drop: Optional[List[str]] = None) -> Dict[Movie, float]:
    lhs_unit_scores_cte = _get_lhs_unit_scores_cte(movie_id=movie_id,
                                                   tags_to_boost=tags_to_boost,
                                                   tags_to_drop=tags_to_drop)
    query_parameters = {
      "lhs_id": movie_id,
      "number_of_results": number_of_results
    }

    if tags_to_boost:
      for i, tag in enumerate(tags_to_boost):
         query_parameters[f"tag_to_boost_{i}"] = tag

    if tags_to_drop:
      for i, tag in enumerate(tags_to_drop):
         query_parameters[f"tag_to_drop_{i}"] = tag

    query = Template(similar_movies_query_template).render(lhs_unit_scores_cte=lhs_unit_scores_cte)

    con = duckdb.connect(":default:")
    con.execute(query, query_parameters)
    result = {}

    for row in con.fetchall():
        movie = Movie(row[0], row[1], row[2])
        result[movie] = row[3] * 100

    return result


@cache
def explain_similarity(lhs_movie_id: int,
                       rhs_movie_id: int,
                       tags_to_boost: Optional[List[str]] = None,
                       tags_to_drop: Optional[List[str]] = None) -> pd.DataFrame:
    lhs_unit_scores_cte = _get_lhs_unit_scores_cte(movie_id=lhs_movie_id,
                                                   tags_to_boost=tags_to_boost,
                                                   tags_to_drop=tags_to_drop)
    query_parameters = {
      "lhs_id": lhs_movie_id,
      "rhs_id": rhs_movie_id
    }

    query = Template(explain_similarity_query).render(lhs_unit_scores_cte=lhs_unit_scores_cte)

    con = duckdb.connect(":default:")
    con.execute(query, query_parameters)
    return con.fetch_df()
