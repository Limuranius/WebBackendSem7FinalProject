from datetime import datetime
from dataclasses import dataclass


@dataclass(frozen=True)
class ProblemTag:
    tag_id: int
    name: str


@dataclass(frozen=True)
class Problem:
    problem_id: int
    name: str
    text: str
    last_used: datetime | None
    tags: list[ProblemTag]

    def find_use_count(self) -> int:
        from .model_read import find_problem_use_count
        return find_problem_use_count(self)


@dataclass(frozen=True)
class TournamentStage:
    stage_id: int
    tournament_id: int
    number: int
    name: str
    problems: list[Problem]


@dataclass(frozen=True)
class Tournament:
    tournament_id: int
    name: str
    description: str
    start_time: datetime
    end_time: datetime
    stages: list[TournamentStage]

    def get_tags(self) -> list[ProblemTag]:
        from .model_read import find_tournament_tags
        return find_tournament_tags(self.tournament_id)
