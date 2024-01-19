from os import path

BASE_DIR = path.dirname(path.abspath(__file__))

MODEL_DIR = path.join(BASE_DIR, "model")
DATABASE_PATH = path.join(MODEL_DIR, "database.db")
CREATE_TABLES_SQL_PATH = path.join(MODEL_DIR, "create tables.sql")

TEMPLATES_DIR = path.join(BASE_DIR, "templates")

DATE_FMT = "%Y-%m-%d"