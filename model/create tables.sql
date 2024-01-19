CREATE TABLE IF NOT EXISTS tournament (
    tournament_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    description TEXT,
    start_time DATETIME,
    end_time DATETIME
);

CREATE TABLE IF NOT EXISTS tournament_stage (
    stage_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tournament_id INTEGER,
    number INTEGER,
    name TEXT,

    FOREIGN KEY (tournament_id) REFERENCES tournament(tournament_id)
);

CREATE TABLE IF NOT EXISTS problem (
    problem_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    text TEXT,
    last_used DATETIME
);

CREATE TABLE IF NOT EXISTS problem_tag (
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
);

CREATE TABLE IF NOT EXISTS problem_tags (
    problem_id INTEGER,
    tag_id INTEGER,

    FOREIGN KEY (problem_id) REFERENCES problem(problem_id),
    FOREIGN KEY (tag_id) REFERENCES problem_tag(tag_id)
);

CREATE TABLE IF NOT EXISTS stage_problems (
    stage_id INTEGER,
    problem_id INTEGER,

    FOREIGN KEY (stage_id) REFERENCES tournament_stage(stage_id),
    FOREIGN KEY (problem_id) REFERENCES problem(problem_id)
);

CREATE TRIGGER IF NOT EXISTS problem_used_trigger
AFTER INSERT ON stage_problems
BEGIN
    UPDATE problem SET last_used = strftime("%s", datetime("now"))
        WHERE problem.problem_id = new.problem_id;
END;
