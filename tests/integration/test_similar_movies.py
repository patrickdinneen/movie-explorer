from movie_explorer import similar_movies
import movie_ids


def test_top_3():
    reference_movies = [movie_ids.THERE_WILL_BE_BLOOD,
                        movie_ids.TOKYO_STORY,
                        movie_ids.LOST_IN_TRANSLATION]
    results = similar_movies.get_similar(reference_movies, number_of_results=3)

    assert set(reference_movies) == set(results.keys())
    assert movie_ids.LOST_IN_TRANSLATION_SIMILAR_MOVIES == set(results.get(movie_ids.LOST_IN_TRANSLATION).keys())
    assert movie_ids.TOKYO_STORY_SIMILAR_MOVIES == set(results.get(movie_ids.TOKYO_STORY).keys())
    assert movie_ids.THERE_WILL_BE_BLOOD_SIMILAR_MOVIES == set(results.get(movie_ids.THERE_WILL_BE_BLOOD).keys())
