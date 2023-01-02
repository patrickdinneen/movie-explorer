from movie_explorer import repository
import movie_explorer.similar_movies
from movie_explorer.model import MovieSimilarity, Movie
from typing import Any, List, Set, Optional


def get_similar(movie_id: int,
                tags_to_boost: Optional[Set[str]] = None,
                tags_to_penalise: Optional[Set[str]] = None) -> MovieSimilarity:
    """
    Returns similar movies. 

    If a calculated similarity exists in Firestore that is used.

    If not then the similarity is calculated and stored.

    But what is the return type? And what happens if nothing exists for that movie id
    """

    similarity_id = MovieSimilarity.create_id(movie_id,
                                              tags_to_boost=tags_to_boost,
                                              tags_to_penalise=tags_to_penalise)
    similarity = repository.get_movie_similarity(similarity_id)
    if similarity:
        print("Cached similarity found. Returning.")
        return similarity
    else:
        print("Similarity not cached. Calculating.")
        similar_movies_result = movie_explorer.similar_movies.get_similar([movie_id],
                                                                          tags_to_boost=tags_to_boost,
                                                                          tags_to_penalise=tags_to_penalise)
        movie = repository.get_movie(movie_id)
        similar_movies = {repository.get_movie(other_movie_id): similarity_score
                          for other_movie_id, similarity_score in similar_movies_result[movie_id].items()}
        similarity = MovieSimilarity(movie,
                                     similar_movies=similar_movies,
                                     tags_to_boost=tags_to_boost,
                                     tags_to_penalise=tags_to_penalise)
        repository.save_movie_similarity(similarity)
        return similarity


def search_movies_by_title(search_string: str) -> List[Movie]:
    return repository.search_by_title(search_string, 10)


def inspect_similarity(reference_movie_id, other_movie_id) -> Any:
    pass
