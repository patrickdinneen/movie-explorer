import duckdb
import streamlit as st
from streamlit_searchbox import st_searchbox
from functools import cache
from typing import List
from movie_explorer.model import Movie
from movie_explorer.similar_movies import get_similar, explain_similarity, get_tags, search_tags

@cache
def search(search_string: str) -> List[Movie]:
    con = duckdb.connect(":default:")
    query_string = """
    SELECT item_id, title, imdb_id 
    FROM 'data/movies.parquet'
    WHERE contains(lower(title), ?)
    LIMIT 20
    """
    con.execute(query_string, [search_string.lower()])
    return [Movie(row[0], row[1], row[2]) for row in con.fetchall()]

  
st.title("Movie Tuner")

st.subheader("Find similar movies")
movie: Movie = st_searchbox(search_function=search, key="searchbox")


if movie:
    st.header(movie.title, divider="rainbow")
    st.markdown(f"[IMDB]({movie.get_imdb_url()})")

    with st.expander("Tune Results"):
        tags_to_drop = st.multiselect("Tags to drop", 
                                      options=get_tags(movie.movie_id))
        tag_to_boost = st_searchbox(search_function=search_tags, key="tags_searchbox")
        if tag_to_boost:
            tags_to_boost = [tag_to_boost]
        else:
            tags_to_boost = []

    similar_movies = get_similar(movie.movie_id, 
                                 tags_to_drop=tags_to_drop,
                                 tags_to_boost=tags_to_boost)
    for similar_movie, score in sorted(similar_movies.items(), 
                                        reverse=True, 
                                        key=lambda x: x[1]):
        st.markdown(f"### {similar_movie.title}")
        st.write(f"Similarity score: {score:.2f}%")
        st.markdown(f"[IMDB]({similar_movie.get_imdb_url()})")
        with st.expander("Explanation"):
            similarity_df = explain_similarity(movie.movie_id,
                                               similar_movie.movie_id,
                                               tags_to_drop=tags_to_drop,
                                               tags_to_boost=tags_to_boost)
            similarity_df.columns = ["Tag", 
                                     movie.title[:25], 
                                     similar_movie.title[:25], 
                                     "Similarity Percentage"]
            st.dataframe(similarity_df,
                         use_container_width=True,
                         hide_index=True)
        # st.button("Show similar", key=similar_movie.movie_id,
        #           on_click=set_movie, args=[similar_movie])
