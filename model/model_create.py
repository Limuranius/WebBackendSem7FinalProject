from .model import conn, cursor
from .objects import *


def create_tag(name: str) -> ProblemTag:
    cursor.execute("""
        INSERT INTO problem_tag (name)
        VALUES (?)
    """, (name,))
    return ProblemTag(
        tag_id=cursor.lastrowid,
        name=name
    )


def create_problem(
        name: str,
        text: str,
        tags: list[ProblemTag]
) -> Problem:
    cursor.execute("""
        INSERT INTO problem (name, text)
        VALUES (?, ?)
    """, (name, text))
    problem_id = cursor.lastrowid
    for tag in tags:
        cursor.execute("""
            INSERT INTO problem_tags
            VALUES (?, ?)
        """, (problem_id, tag.tag_id))
    return Problem(
        problem_id=problem_id,
        name=name,
        text=text,
        last_used=None,
        tags=tags,
    )


def create_tournament(
        name: str,
        description: str,
        start_time: datetime,
        end_time: datetime,
):
    cursor.execute("""
        INSERT INTO tournament (name, description, start_time, end_time)
        VALUES (?, ?, ?, ?)
    """, (name, description,
          int(start_time.timestamp()), int(end_time.timestamp())))
    tournament_id = cursor.lastrowid
    return Tournament(
        tournament_id=tournament_id,
        name=name,
        description=description,
        start_time=start_time,
        end_time=end_time,
        stages=[]
    )


def create_tournament_stage(
        tournament_id: int,
        number: int,
        name: str,
        problems: list[Problem] | list[int]
) -> TournamentStage:
    cursor.execute("""
        INSERT INTO tournament_stage (tournament_id, number, name)
        VALUES (?, ?, ?)
    """, (tournament_id, number, name))
    stage_id = cursor.lastrowid
    for problem in problems:
        if isinstance(problem, Problem):
            problem_id = problem.problem_id
        else:
            problem_id = problem
        cursor.execute("""
            INSERT INTO stage_problems
            VALUES (?, ?)
        """, (stage_id, problem_id))
    return TournamentStage(stage_id, tournament_id, number, name, problems)
