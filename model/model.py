import sqlite3
import settings

conn = sqlite3.connect(settings.DATABASE_PATH, check_same_thread=False)
cursor = conn.cursor()


def create_tables():
    with open(settings.CREATE_TABLES_SQL_PATH, "r") as f:
        cursor.executescript(f.read())
    conn.commit()


def fill_values():
    from .model_create import (
        create_tag,
        create_problem,
        create_tournament,
        create_tournament_stage
    )
    from datetime import datetime

    tag1 = create_tag("Бин. поиск")
    tag2 = create_tag("Математика")
    tag3 = create_tag("Массив")
    tag4 = create_tag("Дерево отрезков")
    tag5 = create_tag("Дерево Фенвика")

    problem1 = create_problem("Задача 1", "Описание задачи 1", [tag1, tag4])
    problem2 = create_problem("Задача 2", "Описание задачи 2", [tag2, tag3])
    problem3 = create_problem("Задача 3", "Описание задачи 3", [tag1, tag2, tag3])
    problem4 = create_problem("Задача 4", "Описание задачи 4", [tag3])
    problem5 = create_problem("Задача 5", "Описание задачи 5", [tag2, tag1])
    problem6 = create_problem("Задача 6", "Описание задачи 6", [tag1])

    tournament1 = create_tournament(
        "ICPC 2024",
        "Международный чемпионат по программированию",
        datetime(2024, 10, 1),
        datetime(2024, 11, 1),
    )
    tournament2 = create_tournament(
        "CWC 2023",
        "Студенческий контест с интересными задачами",
        datetime(2023, 5, 1),
        datetime(2023, 5, 2),
    )

    create_tournament_stage(
        tournament1.tournament_id,
        1,
        "Отборочный этап",
        [problem5]
    )
    create_tournament_stage(
        tournament1.tournament_id,
        2,
        "Полуфинал",
        [problem1, problem2]
    )
    create_tournament_stage(
        tournament1.tournament_id,
        3,
        "Финал",
        [problem3]
    )

    create_tournament_stage(
        tournament2.tournament_id,
        1,
        "Отборочный этап",
        [problem4]
    )
    create_tournament_stage(
        tournament2.tournament_id,
        2,
        "Основной этап",
        [problem5, problem6]
    )
