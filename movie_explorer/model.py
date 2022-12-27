import dataclasses
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional


@dataclass(frozen=True)
class SimilaritySettings:
    minimum_rating: int = 0
    tags_to_boost: Set[str] = field(default_factory=set)
    tags_to_reduce: Set[str] = field(default_factory=set)


@dataclass(frozen=True)
class Movie:
    id: int
    title: str
    imdb_id: int
    starring: str
    directed_by: str

    # similar: Dict[SimilaritySettings, List] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "imdb_id": self.imdb_id,
            "starring": self.starring,
            "directed_by": self.directed_by
        }

    def from_dict(d: Dict):
        return Movie(id=d["id"],
                     title=d["title"],
                     imdb_id=d["imdb_id"],
                     starring=d["starring"],
                     directed_by=d["directed_by"])


# TODO: Batched export/import from BigQuery FML (500 at a time)

@dataclass
class MovieSimilarity:
    movie: Movie
    minimum_rating: Optional[float] = None
    tags_to_boost: Set[str] = field(default_factory=set)
    tags_to_penalise: Set[str] = field(default_factory=set)
    similar_movies: Optional[Dict[Movie, float]] = None

    def get_id(self):
        result = f"movie={self.movie.id}"

        if self.minimum_rating:
            result += f";minimum_rating={self.minimum_rating}"

        if self.tags_to_boost:
            result += f";tags_to_boost={sorted(self.tags_to_boost)}"

        if self.tags_to_penalise:
            result += f";tags_to_penalise={sorted(self.tags_to_penalise)}"

        return result

