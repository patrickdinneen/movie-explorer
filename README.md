# movie-explorer
An Example Critiquing Movie Recommender. 

You can search for a movie and see similar movies. You can optionally make tweaks to example movie you have selected to see different recommendations. As an example, you might search for _In The Mood For Love_ and then tweak the results to be "like _In The Mood For Love_ but with more androids".

You can try the app in action [here](https://movie-explorer-pjd.streamlit.app/)

# Repo guide
I implemented the app using [Streamlit](https://streamlit.io/). 

The Streamlit app is defined in `movie_explorer_app.py`

The main logic of the recommendation is in the module `movie_explorer`. 

`movie_explorer/explorer.py` implements the recommendation logic.

Data is stored in parquet in `data/movies.parquet` and `data/movie_tags.parquet` and is queried using [duckdb](https://duckdb.org/).

# Logic TL;DR

Movie similarity is defined as cosine similarity over tag scores. Applying critiques to an example consists of modifying the tag score for the relevant tag (either increasing or decreasing it, as required).

Tags are stored as `(movie_id, tag, score, unit_score)` rather than a wide table, which would be very sparse and annoying to join.

The cosine similarity can then be implemented as an inner join on movie and tag and taking the sum of products.
