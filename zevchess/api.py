import flask

from zevchess.commands import update_existing_uids_cache, create_game as create_a_game
from zevchess.queries import get_existing_uids_from_db

# TODO: limit the number of concurrent games based on load testing
# TODO: limit the number of games for a given IP address


application = flask.Flask(__name__)


@application.route("/create_game", methods=["POST"])
def create_game() -> flask.Response:
    uid = create_a_game()
    return flask.jsonify({"uid": uid})


def main():
    # cache the existing UIDs
    uids = get_existing_uids_from_db()
    update_existing_uids_cache(*uids)
