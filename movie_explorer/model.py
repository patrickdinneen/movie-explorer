from dataclasses import dataclass, field
from typing import List, Dict, Set


@dataclass(frozen=True)
class SimilaritySettings:
    minimum_rating: int = 0
    tags_to_boost: Set[str] = field(default_factory=set)
    tags_to_reduce: Set[str] = field(default_factory=set)


@dataclass
class Movie:
    id: int
    title: str
    imdb_id: int
    starring: str
    directed_by: str
    # similar: Dict[SimilaritySettings, List] = field(default_factory=dict)
