from flask import Flask

app = Flask(__name__)
app.secret_key = "123"
session = dict()
from controllers import (
    tournaments,
    create,
    choose_problem
)
