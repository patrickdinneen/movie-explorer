from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional
from pprint import pformat


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
    tags: List[str] = field(default_factory=list)

    # similar: Dict[SimilaritySettings, List] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "imdb_id": self.imdb_id,
            "starring": self.starring,
            "directed_by": self.directed_by,
            "tags": self.tags
        }

    @classmethod
    def from_dict(cls, d: Dict):
        return Movie(id=d["id"],
                     title=d["title"],
                     imdb_id=d["imdb_id"],
                     starring=d["starring"],
                     directed_by=d["directed_by"],
                     tags=d["tags"])

    def __repr__(self) -> str:
        return f"{self.title} (id: {self.id})\ntags: {pformat(self.tags)}"

    def __hash__(self) -> int:
        return hash(self.id)


@dataclass
class MovieSimilarity:
    movie: Movie
    minimum_rating: Optional[float] = None
    tags_to_boost: Optional[Set[str]] = None
    tags_to_penalise: Optional[Set[str]] = None
    similar_movies: Dict[Movie, float] = field(default_factory=dict)

    def get_id(self):
        return MovieSimilarity.create_id(self.movie.id,
                                         self.minimum_rating,
                                         self.tags_to_boost,
                                         self.tags_to_penalise)

    @classmethod
    def create_id(cls, movie_id: int,
                  minimum_rating: Optional[float] = None,
                  tags_to_boost: Optional[Set[str]] = None,
                  tags_to_penalise: Optional[Set[str]] = None) -> str:
        result = f"movie={movie_id}"

        if minimum_rating:
            result += f";minimum_rating={minimum_rating}"

        if tags_to_boost:
            result += f";tags_to_boost={sorted(tags_to_boost)}"

        if tags_to_penalise:
            result += f";tags_to_penalise={sorted(tags_to_penalise)}"

        return result

    def __repr__(self) -> str:
        similarity_scores = {m.title: score
                             for m, score in self.similar_movies.items()}
        return f"Similar movies to {self.movie.title}\n{pformat(similarity_scores)}"
