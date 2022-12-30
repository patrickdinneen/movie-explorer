from google.cloud import firestore
from typing import List, Optional, Dict
from google.cloud.firestore_v1 import CollectionReference, DocumentReference

from movie_explorer.model import Movie, MovieSimilarity

client = firestore.Client()


def get_movie(movie_id: int) -> Movie:
    """
    Retrieves a movie by id.

    Raises an error if the movie does not exist.
    """
    movie_document_ref = _get_movie_document(movie_id)

    document_dict = movie_document_ref.get().to_dict()
    if document_dict:
        return Movie.from_dict(document_dict)
    else:
        raise ValueError(f"Movie not found: id [{movie_id}]")


def _get_movie_document(movie_id) -> DocumentReference:
    return _get_movies().document(str(movie_id))


def write_movies(movies: List[Movie]):
    """
    Save changes to movie.

    Movies that do not exist will be inserted.
    """
    batch = client.batch()
    for movie in movies:
        movie_document = _get_movie_document(movie.id)
        movie_dict = movie.to_dict()
        movie_dict["title_lower"] = movie.title.lower()
        batch.set(movie_document, movie_dict)
    
    batch.commit()


def search_by_title(title: str, max_results: int = 10) -> List[Movie]:
    """
    Searches for movies by title
    """
    # client.collection(u"movies").where()
    title_as_lower = title.lower()
    docs = _get_movies().where("title_lower", ">", title_as_lower).where("title_lower", "<",
                                                                         title_as_lower + "z").limit(
        max_results).order_by("title_lower")

    return [Movie.from_dict(doc.to_dict()) for doc in docs.stream()]


def delete_movie(movie: Movie):
    """
    Deletes a movie
    """
    _get_movies().document(str(movie.id)).delete()


def _get_movies() -> CollectionReference:
    return client.collection(u"movies")


def _get_movies_similarities() -> CollectionReference:
    return client.collection(u"movie_similarities")


def save_movie_similarity(similarity: MovieSimilarity):
    similarity_document = _get_movies_similarities().document(similarity.get_id())
    similarity_document.set(_similarity_to_dict(similarity))


def _similarity_to_dict(similarity: MovieSimilarity) -> Dict:
    similar_movies = {_get_movie_document(movie.id).path: score
                      for movie, score in similarity.similar_movies.items()}

    return {
        "movie": _get_movie_document(similarity.movie.id).path,
        "minimum_rating": similarity.minimum_rating,
        "tags_to_boost": similarity.tags_to_boost,
        "tags_to_penalise": similarity.tags_to_penalise,
        "similar_movies": similar_movies
    }


def _dict_to_similarity(d: Dict) -> MovieSimilarity:
    similar_movies = {Movie.from_dict(client.document(doc).get().to_dict()): similarity_score
                      for doc, similarity_score in d["similar_movies"].items()}
    return MovieSimilarity(movie=Movie.from_dict(client.document(d["movie"]).get().to_dict()),
                           minimum_rating=d.get("minimum_rating"),
                           tags_to_boost=set(d.get("tags_to_boost")),
                           tags_to_penalise=set(d.get("tags_to_penalise")),
                           similar_movies=similar_movies)


def get_movie_similarity(movie_similarity_id: str) -> Optional[MovieSimilarity]:
    similarity_doc = _get_movies_similarities().document(movie_similarity_id)

    doc_dict = similarity_doc.get().to_dict()
    if doc_dict:
        return _dict_to_similarity(doc_dict)
    else:
        return None


def delete_movie_similarity(movie_similarity_id: str):
    _get_movies_similarities().document(movie_similarity_id).delete()
