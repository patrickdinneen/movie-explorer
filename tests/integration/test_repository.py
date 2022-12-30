from movie_explorer import repository
from movie_explorer.model import Movie, MovieSimilarity
import pytest
import random


@pytest.fixture()
def lost_in_translation():
    movie = _create_random_id_movie("Lost In Translation")
    repository.write_movies([movie])
    yield movie
    repository.delete_movie(movie)


@pytest.fixture()
def lord_of_the_rings():
    movie = _create_random_id_movie("Lord Of The Rings")
    repository.write_movies([movie])
    yield movie
    repository.delete_movie(movie)


@pytest.fixture()
def ghostbusters():
    movie = _create_random_id_movie("Ghostbusters")
    repository.write_movies([movie])
    yield movie
    repository.delete_movie(movie)


def test_get_movie_error():
    with pytest.raises(ValueError):
        repository.get_movie(1)


def test_save_movie():
    random_movie = _create_random_id_movie("Random Save Movie")
    repository.write_movies([random_movie])
    retrieved_movie = repository.get_movie(random_movie.id)
    assert random_movie == retrieved_movie
    repository.delete_movie(random_movie)


def test_delete_movie():
    any_old_movie = _create_random_id_movie("Random Delete Movie")
    repository.write_movies([any_old_movie])

    repository.delete_movie(any_old_movie)

    with pytest.raises(ValueError):
        repository.get_movie(any_old_movie.id)


def test_search(ghostbusters, lost_in_translation, lord_of_the_rings):
    assert repository.search_by_title("lo") == [lord_of_the_rings, lost_in_translation]
    assert repository.search_by_title("lo", max_results=1) == [lord_of_the_rings]
    assert repository.search_by_title("los") == [lost_in_translation]
    assert repository.search_by_title("ost") == []


def _create_random_id_movie(title, tags=None) -> Movie:
    return Movie(random.randint(-100000, 0), title, random.randint(-100000, 0), "", "", tags=tags)


def test_save_get_movie_similarity(ghostbusters, lost_in_translation, lord_of_the_rings):
    similarity = MovieSimilarity(ghostbusters,
                                 0.7,
                                 {"fantasy", "tokyo"},
                                 {"ghosts"},
                                 {
                                     lost_in_translation: 0.72,
                                     lord_of_the_rings: 0.61,
                                 })

    try:
        repository.save_movie_similarity(similarity)
        loaded_similarity = repository.get_movie_similarity(similarity.get_id())
        assert similarity == loaded_similarity
    finally:
        repository.delete_movie_similarity(similarity.get_id())