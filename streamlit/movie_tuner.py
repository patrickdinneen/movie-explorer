import duckdb
import streamlit as st
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class Movie:
    movie_id: int
    movie_title: str
    imdb_id: int | None = None

    def __repr__(self) -> str:
        return f"{self.movie_title} (id: {self.movie_id})"

def search(search_string: str) -> List[Movie]:
    con = duckdb.connect(':default:')
    query_string = """
    SELECT item_id, title, imdb_id 
    FROM 'data/movies.parquet'
    WHERE contains(lower(title), ?)
    LIMIT 20
    """
    con.execute(query_string, [search_string.lower()])
    return [Movie(row[0], row[1], row[2]) for row in con.fetchall()]


st.title("Movie Tuner")

search_input = st.text_input("Search")
search_result = search(search_input)

st.write(f"Results {search_result}")
