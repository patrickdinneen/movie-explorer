import streamlit as st
from dataclasses import dataclass
from streamlit_searchbox import st_searchbox
from movie_explorer.model import Movie
from movie_explorer import explorer

@dataclass
class ScoreQuality:
    quality: str
    text_colour: str

    @classmethod
    def get_score_quality(cls, score: float) -> "ScoreQuality":
        if score > 65.0:
            return ScoreQuality("Excellent", "rainbow")
        elif score > 60.0:
            return ScoreQuality("Strong", "green")
        elif score > 50.0:
            return ScoreQuality("Average", "orange")
        else:
            return ScoreQuality("Weak", "grey")

main_help = """Search for a movie to see similar movies.
            Fine-tune the results to discover movies that are more like _X_ and less like _Y_."""
st.title("Movie Explorer", help=main_help)

app, about = st.tabs(["App", "About"])

with app:
    st.subheader("Find similar movies")
    st.markdown("_Note: Only movies released before 2022_")
    movie: Movie = st_searchbox(search_function=explorer.search, 
                                key="searchbox")


    if movie:
        st.header(movie.title)
        st.markdown(f"[IMDB]({movie.get_imdb_url()})")

        with st.expander("**Fine-tune Results**"):
            st.markdown("For best results apply multiple changes")
            movie_tags = explorer.get_tags(movie.movie_id)
            tags_to_drop = st.multiselect("Less like", options=movie_tags)
            tags_not_present = [t for t in explorer.get_all_tags() if t not in movie_tags]
            tags_to_boost = st.multiselect("More like", options=tags_not_present)

        st.subheader("Similar Movies", divider="rainbow")

        similar_movies = explorer.get_similar(movie.movie_id,
                                            tags_to_drop=tags_to_drop,
                                            tags_to_boost=tags_to_boost)
        for similar_movie, score in sorted(similar_movies.items(), 
                                        reverse=True, 
                                        key=lambda x: x[1]):
            score_quality = ScoreQuality.get_score_quality(score)
            st.markdown(f"### {similar_movie.title}")
            st.markdown(f":{score_quality.text_colour}[Similarity score: {score:.2f}]")
            st.markdown(f"Similarity strength: {score_quality.quality}")
            st.markdown(f"[IMDB]({similar_movie.get_imdb_url()})")
            with st.expander("*Explain similarity score*"):
                st.write("""The table below shows the tags and tag scores for each movie.                        
                            The more tags movies share at similar tag scores, the higher the similarity.""")
                similarity_df = explorer.explain_similarity(movie.movie_id,
                                                            similar_movie.movie_id,
                                                            tags_to_drop=tags_to_drop,
                                                            tags_to_boost=tags_to_boost)
                similarity_df.columns = ["Tag",
                                        movie.title[:25],
                                        similar_movie.title[:25],
                                        "Similarity score points"]
                st.dataframe(similarity_df, use_container_width=True, hide_index=True)

with about:
    st.subheader("What Movie Explorer does", divider="red")
    st.markdown("Movie Explorer allows you to search for movies and find similar movies.")
    st.markdown("You can fine-tune the similarity by specifying tags to include and/or exclude.")
    st.markdown("This allows you to search for movies that are, for example, \"Like 'Fistful of Dollars' but with more samurai\".")
    
    st.subheader("What the similarity score means", divider="red")                
    st.markdown("Similarity is calculated based on the tags for each pair of movies and the scores for those tags.")
    st.markdown("If two movies have exactly the same tags with the same tag scores then the similarity score for the pair will be 100.")
    st.markdown("You can view the detailed breakdown of each similarity score by clicking on 'Explain similarity score'.")

    st.subheader("Why can't I find some movies?", divider="red")                
    st.markdown("The dataset used only contains about 8000 movies and doesn't have movies made after 2021.")

    st.subheader("How to improve fine-tuning results", divider="red")
    st.markdown("If you inspect the score breakdown for a movie you may notice that single tags only contribute a small amount to the overall score.")
    st.markdown("As a result, when you add/remove a single tag the resulting scores only change by small amounts. Try using more tags.")

    st.subheader("Dataset", divider="red")
    st.markdown("This tool uses the [MovieLens Tag Genome Dataset 2021](https://grouplens.org/datasets/movielens/tag-genome-2021/) made available by Grouplens.")

    st.subheader("Some of the tags are weird", divider="red")
    st.markdown("The tags available in the dataset are community contributed and do not reflect the personal values of the author of Movie Explorer.")