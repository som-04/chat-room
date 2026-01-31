from flask import Blueprint, redirect, render_template, request, session, url_for

from .state import generate_unique_code, rooms

bp = Blueprint("main", __name__)


@bp.route("/", methods=["POST", "GET"])
def home():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        if not name:
            return render_template(
                "home.html", error="Please enter a name.", code=code, name=name
            )

        if join is not False and not code:
            return render_template(
                "home.html", error="Please enter a room code.", code=code, name=name
            )

        room = code
        if create is not False:
            room = generate_unique_code(4)
            rooms[room] = {"members": 0, "messages": [], "peers": {}}
        elif code not in rooms:
            return render_template(
                "home.html", error="Room does not exist.", code=code, name=name
            )
        session["room"] = room
        session["name"] = name
        return redirect(url_for("main.room"))

    return render_template("home.html")


@bp.route("/room")
def room():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("main.home"))

    return render_template("room.html", code=room, messages=rooms[room]["messages"])
