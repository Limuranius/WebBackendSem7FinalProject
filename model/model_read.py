from .model import conn, cursor
import pandas as pd
from datetime import datetime
from .objects import *


def all_tags() -> list[ProblemTag]:
    cursor.execute("""
        SELECT *
        FROM problem_tag
    """)
    return list(map(
        lambda row: ProblemTag(row[0], row[1]),
        cursor.fetchall()
    ))


def find_problem_tags(problem_id: int) -> list[ProblemTag]:
    script = """
        SELECT tag_id, name
        FROM problem_tag
        JOIN problem_tags
        USING (tag_id)
        WHERE problem_id = :problem_id
    """
    cursor.execute(script, {
        "problem_id": problem_id
    })
    return list(map(
        lambda row: ProblemTag(row[0], row[1]),
        cursor.fetchall()
    ))


def find_tournament_tags(tournament_id: int) -> list[ProblemTag]:
    cursor.execute("""
        SELECT DISTINCT problem_tag.tag_id, problem_tag.name
        FROM problem_tag
        JOIN problem_tags USING (tag_id)
        JOIN problem USING (problem_id)
        JOIN stage_problems USING (problem_id)
        JOIN tournament_stage USING (stage_id)
        JOIN tournament USING (tournament_id)
        WHERE tournament_id = ?
    """, (tournament_id,))
    return list(map(
        lambda row: ProblemTag(row[0], row[1]),
        cursor.fetchall()
    ))


def find_tournaments(
        start: datetime = None,
        end: datetime = None,
        tags: list[ProblemTag] = None,
) -> list[Tournament]:
    conditions = []
    args = []

    if tags:
        tags_count = len(tags) if tags else 0
        tags_sql_list = ",".join(["(?)"] * tags_count)
        if tags:
            for tag in tags:
                args.append(tag.tag_id)
        args.append(tags_count)
        conditions.append("tournament_id IN tag_match_tournaments")

    if start:
        conditions.append("(? < tournament.start_time)")
        args.append(start.timestamp())
    if end:
        conditions.append("(tournament.end_time < ?)")
        args.append(end.timestamp())

    condition = ""
    if conditions:
        condition = "WHERE " + " AND ".join(conditions)

    if tags:
        sql = f"""
            WITH 
            tournament_tags(tournament_id, tag_id) 
            AS (
                SELECT DISTINCT tournament_id, tag_id
                FROM tournament
                JOIN tournament_stage USING (tournament_id)
                JOIN stage_problems USING (stage_id)
                JOIN problem USING (problem_id)
                JOIN problem_tags USING (problem_id)
            ),
            search_tags(tag_id)
            AS (
                VALUES {tags_sql_list}
            ),
            tournament_search_match_count(tournament_id, match_count)
            AS (
                SELECT tournament_id, COUNT(*)
                FROM tournament_tags
                JOIN search_tags USING (tag_id)
                GROUP BY (tournament_id)
            ),
            tag_match_tournaments(tournament_id)
            AS (
                SELECT tournament_id
                FROM tournament_search_match_count
                WHERE match_count >= ?
            )
            SELECT 
                tournament.tournament_id,
                tournament.name,
                tournament.description,
                tournament.start_time,
                tournament.end_time,
                tournament_stage.stage_id,
                tournament_stage.name,
                tournament_stage.number,
                problem.problem_id,
                problem.name,
                problem.text,
                problem.last_used,
                problem_tag.tag_id,
                problem_tag.name
            FROM tournament
            JOIN tournament_stage USING (tournament_id)
            JOIN stage_problems USING (stage_id)
            JOIN problem USING (problem_id)
            JOIN problem_tags USING (problem_id)
            JOIN problem_tag USING (tag_id)
            {condition}
        """
    else:
        sql = f"""
            SELECT 
                tournament.tournament_id,
                tournament.name,
                tournament.description,
                tournament.start_time,
                tournament.end_time,
                tournament_stage.stage_id,
                tournament_stage.name,
                tournament_stage.number,
                problem.problem_id,
                problem.name,
                problem.text,
                problem.last_used,
                problem_tag.tag_id,
                problem_tag.name
            FROM tournament
            JOIN tournament_stage USING (tournament_id)
            JOIN stage_problems USING (stage_id)
            JOIN problem USING (problem_id)
            JOIN problem_tags USING (problem_id)
            JOIN problem_tag USING (tag_id)
            {condition}
        """
    print(sql)
    print(args)
    df = pd.read_sql(sql, conn, params=args)
    df.columns = [
        "tour_id", "tour_name", "tour_description", "tour_start_time", "tour_end_time",
        "stage_id", "stage_name", "stage_number",
        "problem_id", "problem_name", "problem_text", "problem_last_used",
        "tag_id", "tag_name"
    ]

    tournaments = []
    for tournament_id, tournament_rows in df.groupby(["tour_id"]):
        tour_row = tournament_rows.iloc[0]
        tour_name = tour_row["tour_name"]
        tour_description = tour_row["tour_description"]
        tour_start_time = datetime.fromtimestamp(tour_row["tour_start_time"])
        tour_end_time = datetime.fromtimestamp(tour_row["tour_end_time"])
        stages = []
        for stage_id, stage_rows in tournament_rows.groupby(["stage_id"]):
            st_row = stage_rows.iloc[0]
            st_number = st_row["stage_number"]
            st_name = st_row["stage_name"]
            problems = []
            for problem_id, problem_rows in stage_rows.groupby(["problem_id"]):
                prob_row = problem_rows.iloc[0]
                prob_name = prob_row["problem_name"]
                prob_text = prob_row["problem_text"]
                prob_last_used = datetime.fromtimestamp(prob_row["problem_last_used"])
                tags = []
                for _, row in problem_rows.iterrows():
                    tag_id = row["tag_id"]
                    tag_name = row["tag_name"]
                    tags.append(ProblemTag(tag_id, tag_name))
                problems.append(Problem(
                    problem_id[0],
                    prob_name,
                    prob_text,
                    prob_last_used,
                    tags
                ))
            stages.append(TournamentStage(
                stage_id[0],
                tournament_id[0],
                st_number,
                st_name,
                problems
            ))
        tournaments.append(Tournament(
            tournament_id[0],
            tour_name,
            tour_description,
            tour_start_time,
            tour_end_time,
            stages
        ))
    return tournaments


def get_problem(problem_id: int) -> Problem:
    tags = find_problem_tags(problem_id)
    cursor.execute("""
        SELECT name, text, last_used
        FROM problem
        WHERE problem_id = ?
    """, (problem_id, ))
    row = cursor.fetchone()
    name = row[0]
    text = row[1]
    last_used = datetime.fromtimestamp(row[2])
    return Problem(problem_id, name, text, last_used, tags)


def find_problems(tag_ids: list[int]) -> list[Problem]:
    if len(tag_ids) == 0:
        sql = """
            SELECT problem_id
            FROM problem
        """
        args = []
    else:
        tags_count = len(tag_ids) if tag_ids else 0
        tags_sql_list = ",".join(["(?)"] * tags_count)
        sql = f"""
            WITH
            search_tags(tag_id)
            AS (
                VALUES {tags_sql_list}
            ),
            problem_match_count(problem_id, match_count)
            AS (
                SELECT problem_id, COUNT(*)
                FROM problem_tags
                JOIN search_tags USING (tag_id)
                GROUP BY (problem_id)
            )
            SELECT problem_id
            FROM problem_match_count
            WHERE match_count >= ?
        """
        args = tag_ids + [tags_count]

    cursor.execute(sql, args)
    return [get_problem(problem_id[0]) for problem_id in cursor.fetchall()]


def get_tag(tag_id: int) -> ProblemTag:
    cursor.execute("""
        SELECT tag_id, name
        FROM problem_tag
        WHERE tag_id = ?
    """, (tag_id, ))
    row = cursor.fetchone()
    return ProblemTag(row[0], row[1])


def find_problem_use_count(problem: Problem) -> int:
    cursor.execute("""
        SELECT COUNT(*)
        FROM stage_problems
        WHERE problem_id = ?
    """, (problem.problem_id,))
    return cursor.fetchone()[0]