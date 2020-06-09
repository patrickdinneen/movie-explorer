from google.cloud import bigquery
from google.cloud import storage
from os import path
import tempfile
import subprocess
import uuid


def export_query_to_sqlite(sql, storage_folder_uri, sqlite_db_filename, destination_table, delete_table=True):
    bq_client = bigquery.Client()
    job_config = bigquery.QueryJobConfig()
    job: bigquery.QueryJob = bq_client.query(sql, job_config=job_config)
    job.result()
    export_table_to_sqlite(job.destination, storage_folder_uri,
                           sqlite_db_filename, destination_table, delete_table)


def export_table_to_sqlite(fully_qualified_table_name, storage_folder_uri,
                           sqlite_db_filename, destination_table, delete_table=True):
    bq_client = bigquery.Client()
    storage_uri = path.join(storage_folder_uri, str(uuid.uuid4()))
    extract_config = bigquery.ExtractJobConfig()
    extract_config.field_delimiter = '|'
    extract_job = bq_client.extract_table(fully_qualified_table_name, storage_uri, job_config=extract_config)
    extract_job.result()
    print('Extract complete')
    import_table_to_sqlite(storage_uri, sqlite_db_filename, destination_table, delete_table)


def import_table_to_sqlite(storage_uri, sqlite_db_filename, destination_table, delete_table):
    storage_client = storage.Client()
    with tempfile.NamedTemporaryFile() as f:
        storage_client.download_blob_to_file(storage_uri, f)
        sqlite_import_csv(sqlite_db_filename, destination_table, f.name, delete_table)
    print('Load complete')


def sqlite_import_csv(sqlite_db_filename, table, csv_filename, delete_table=False):
    sqlite3_commands = []

    if delete_table:
        sqlite3_commands.insert(0, 'drop table {};'.format(table))
        sqlite3_commands.append('.import {csv_filename} {table}'.format(csv_filename=csv_filename,
                                                                        table=table))
    else:
        sqlite3_commands.append('.import \'| tail -n +2 {csv_filename}\' {table}'.format(csv_filename=csv_filename,
                                                                        table=table))

    sqlite3_import_string = '\n'.join(sqlite3_commands)
    print(sqlite3_import_string)
    echo = subprocess.Popen(['echo', sqlite3_import_string], stdout=subprocess.PIPE)
    sqlite_import = subprocess.Popen(['sqlite3', sqlite_db_filename], stdin=echo.stdout, stdout=subprocess.PIPE)
    sqlite_import.communicate()


if __name__ == '__main__':
    genome_query = '''
    SELECT
        *
    FROM `pjdmovies.movielens.genome_scores_unit`
    WHERE movie_id IN (SELECT movie_id FROM `pjdmovies.movielens.movie_similarities`)
        OR movie_id IN (SELECT DISTINCT other_movie_id FROM `pjdmovies.movielens.movie_similarities`)
    '''
    export_query_to_sqlite(genome_query, 'gs://pjdmovies-movielens/exports',
                           'var/db/movie-explorer.db', 'genome_scores')

    movie_query = '''
    SELECT
      movies.*,
      movie_links.imdb_id,
      movie_links.tmdbs_id 
    FROM `pjdmovies.movielens.movies` movies
    INNER JOIN `pjdmovies.movielens.movie_links` movie_links
    ON movies.movie_id = movie_links.movie_id    
    '''
    export_query_to_sqlite(movie_query, 'gs://pjdmovies-movielens/exports',
                           'var/db/movie-explorer.db', 'movies')

    export_table_to_sqlite('pjdmovies.movielens.movie_similarities', 'gs://pjdmovies-movielens/exports',
                           'var/db/movie-explorer.db', 'movie_similarities')

    export_table_to_sqlite('pjdmovies.movielens.tags', 'gs://pjdmovies-movielens/exports',
                           'var/db/movie-explorer.db', 'tags')

    export_table_to_sqlite('pjdmovies.movielens.tag_weights', 'gs://pjdmovies-movielens/exports',
                           'var/db/movie-explorer.db', 'tag_weights')
