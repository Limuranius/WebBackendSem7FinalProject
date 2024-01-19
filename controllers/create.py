from datetime import datetime
from app import app, session
import model
from flask import render_template, request, redirect, url_for
import settings


@app.route('/create', methods=['get'])
def create_get():
    if not session.get("create_process"):
        session["tournament_name"] = ""
        session["stages"] = []
        session["description"] = ""
        session["start_time"] = datetime.now()
        session["end_time"] = datetime.now()
        session["create_process"] = True

    if request.values.get("action") == "Добавить этап":
        stage_name = request.values["stage_name"]
        stage = model.TournamentStage(None, None, None, stage_name, [])
        session["stages"].append(stage)
    elif request.values.get("action") == "Добавить задачу":
        stage_idx = int(session["stage_idx"])
        problem_id = int(request.values["problem_id"])
        problem = model.get_problem(problem_id)
        session["stages"][stage_idx].problems.append(problem)

    return render_template(
        "create_tournament.html",
        stages=session["stages"],
    )


@app.route('/create', methods=['post'])
def create_post():
    tournament_name = request.values["tournament_name"]
    description = request.values["description"]
    start_time = datetime.strptime(request.values["start_time"], settings.DATE_FMT)
    end_time = datetime.strptime(request.values["end_time"], settings.DATE_FMT)

    created_tournament = model.create_tournament(
        tournament_name,
        description,
        start_time,
        end_time
    )

    for i, stage in enumerate(session["stages"]):
        model.create_tournament_stage(
            created_tournament.tournament_id,
            i + 1,
            stage.name,
            stage.problems
        )

    del session["create_process"]
    print(url_for("tournaments"))
    return redirect(url_for("tournaments"))
