from app import app, session
import model
from flask import render_template, request, redirect


@app.route('/problems', methods=['get'])
def choose_problem():
    if request.values.get("stage_idx"):
        session["stage_idx"] = request.values.get("stage_idx", type=int)

    used_tags = request.values.getlist("used_tags", type=int)
    used_tags = [model.get_tag(tag_id) for tag_id in used_tags]
    unused_tags = set(model.all_tags()) - set(used_tags)

    if request.values.get("add_tag"):
        tag_id = request.values.get("tag", type=int)
        tag = model.get_tag(tag_id)
        used_tags.append(tag)
        unused_tags -= {tag, }

    problems = model.find_problems([tag.tag_id for tag in used_tags])

    return render_template(
        "choose_problem.html",
        problems=problems,
        used_tags=used_tags,
        unused_tags=unused_tags
    )
