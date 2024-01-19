from datetime import datetime
import settings
from app import app
import model
from flask import render_template, request


@app.route('/', methods=['get'])
def tournaments():
    search_kwargs = dict()
    used_tags = request.values.getlist("used_tags", type=int)
    used_tags = [model.get_tag(tag_id) for tag_id in used_tags]
    unused_tags = set(model.all_tags()) - set(used_tags)
    search_kwargs["tags"] = used_tags

    if request.values.get("add_tag"):
        tag_id = request.values.get("tag", type=int)
        tag = model.get_tag(tag_id)
        used_tags.append(tag)
        unused_tags -= {tag, }

    if request.values.get("search"):
        start_time = request.values.get("start_time")
        if start_time:
            search_kwargs["start"] = datetime.strptime(start_time, settings.DATE_FMT)
        end_time = request.values.get("end_time")
        if end_time:
            search_kwargs["end"] = datetime.strptime(end_time, settings.DATE_FMT)

    tours = model.find_tournaments(**search_kwargs)

    html = render_template(
        'tournaments.html',
        tournaments=tours,
        used_tags=used_tags,
        unused_tags=unused_tags
    )
    return html
