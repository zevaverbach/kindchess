import flask

from zevchess import queries as q
from zevchess import commands as c

# TODO: limit the number of concurrent games based on load testing
# TODO: limit the number of games for a given IP address


application = flask.Flask(__name__)


@application.route("/create_game", methods=["POST"])
def create_game() -> flask.Response:
    uid = c.create_game()
    return flask.jsonify({"uid": uid})


@application.route("/")
def home() -> str:
    active_games = q.get_active_game_uids()
    return flask.render_template("home.html", active_games=active_games)


@application.route("/<string: uid>")
def game(uid: str) -> str:
    if not q.uid_exists_and_is_an_active_game(uid):
        return flask.render_template("no_such_game.html", uid=uid)
    return flask.render_template("game.html", uid=uid)



def main():
    # cache the UIDs of active games
    c.update_existing_uids_cache(*q.get_active_game_uids())
