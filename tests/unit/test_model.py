from movie_explorer.model import Movie, MovieSimilarity


def test_get_id():
    movie = Movie(123, "", 0, "", "")

    bare_similarity = MovieSimilarity(movie)
    assert bare_similarity.get_id() == "movie=123"

    minimum_rating_similarity = MovieSimilarity(movie, minimum_rating=7.3)
    assert minimum_rating_similarity.get_id() == "movie=123;minimum_rating=7.3"

    tags_to_boost = MovieSimilarity(movie, tags_to_boost={"mystery", "drama", "action"})
    assert tags_to_boost.get_id() == "movie=123;tags_to_boost=['action', 'drama', 'mystery']"

    the_works = MovieSimilarity(movie,
                                minimum_rating=8.1,
                                tags_to_boost={"mystery", "drama", "action"},
                                tags_to_penalise={"horror", "adventure"})
    assert the_works.get_id() == "movie=123;minimum_rating=8.1;tags_to_boost=['action', 'drama', 'mystery'];" \
                                 "tags_to_penalise=['adventure', 'horror']"
