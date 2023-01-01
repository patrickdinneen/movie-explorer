from google.cloud import bigquery
from movie_explorer.model import Movie
from movie_explorer import repository


movies_query = """
WITH top_n_tags AS (
  SELECT
    item_id,
    tag,
    unit_score,
    ROW_NUMBER() OVER (PARTITION BY item_id ORDER BY unit_score DESC) as row_num
  FROM movielens.movie_tags_unit_score
) 
SELECT
  m.item_id as id,
  m.title,
  m.imdbId as imdb_id,
  m.starring,
  m.directedBy as directed_by,
  STRING_AGG(top_n_tags.tag, ';' ORDER BY top_n_tags.unit_score DESC) as top_tags
FROM movielens.movies m
INNER JOIN top_n_tags ON m.item_id = top_n_tags.item_id
AND top_n_tags.row_num < 30
GROUP BY 1, 2, 3, 4, 5
"""


def import_all():
    client = bigquery.Client()
    movie_rows = client.query(movies_query)

    movie_counter = 0
    batch = []

    for row in movie_rows:
        movie = Movie(id=row["id"],
                      title=row["title"], 
                      imdb_id=row["imdb_id"],
                      starring=row["starring"],
                      directed_by=row["directed_by"],
                      tags=row["top_tags"].split(";"))
        batch.append(movie)
        # repository.write_movies(movie)
        if len(batch) == 500:
          repository.write_movies(batch)
          batch = []
        movie_counter += 1
        if movie_counter % 100 == 0:
            print(f"Saved movie count: {movie_counter}")

    if batch:  # write the last batch
      repository.write_movies(batch)


if __name__ == "__main__":
    import_all()
