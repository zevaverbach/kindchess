import os
import pathlib as pl

import flask

from zevchess import queries as q
from zevchess import commands as c

# TODO: limit the number of concurrent games based on load testing
# TODO: limit the number of games for a given IP address


application = flask.Flask(__name__)


@application.route("/")
def home() -> str:
    print("home")
    active_games = q.get_active_game_uids()
    print(f"{active_games=}")
    return flask.render_template("home.html", active_games=active_games)


@application.route("/<string:uid>")
def game(uid: str) -> str:
    print(f"{uid=}")
    if uid.strip() == "":
        active_games = q.get_active_game_uids()
        print(f"{active_games=}")
        return flask.render_template("home.html", active_games=active_games)
    if not q.uid_exists_and_is_an_active_game(uid):
        return flask.render_template("no_such_game.html", uid=uid)
    return flask.render_template("game.html", uid=uid)


@application.route("/create_game", methods=["POST"])
def create_game() -> flask.Response:
    uid = c.create_game()
    print("created a game", uid)
    return flask.jsonify({"uid": uid})


@application.route("/favicon.ico")
def favicon():
    return flask.send_from_directory(
        pl.Path(application.root_path) / "static",
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@application.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == "static":
        filename = values.get("filename", None)
        if filename:
            file_path = os.path.join(application.root_path, endpoint, filename)
            values["q"] = int(os.stat(file_path).st_mtime)
    return flask.url_for(endpoint, **values)


def main():
    # cache the UIDs of active games
    c.update_existing_uids_cache(*q.get_active_game_uids())
