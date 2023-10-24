from dataclasses import dataclass


@dataclass(frozen=True, eq=True)
class Movie:
    movie_id: int
    title: str
    imdb_id: int

    def __repr__(self) -> str:
        return self.title

    def get_imdb_url(self) -> str:
        return f"https://www.imdb.com/title/tt{self.imdb_id:07d}/"
