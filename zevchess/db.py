import atexit
import os

from dotenv import load_dotenv
import psycopg2
import redis
from rich.pretty import pprint

PROD = os.getenv("ZEVCHESS_PROD")

match PROD:
    case 1 | '1':
        dotenv_path = ".env"
        REDIS_URL_ENV_VAR = "REDIS_URL"
        DB_HOSTNAME_ENV_VAR = "DB_HOSTNAME"
    case 0 | '0':
        dotenv_path = ".env-dev"
        REDIS_URL_ENV_VAR = "REDIS_URL_PUBLIC"
        DB_HOSTNAME_ENV_VAR = "DB_HOSTNAME_PUBLIC"
    case _:
        raise Exception

load_dotenv(dotenv_path)
REDIS_URL = os.getenv(REDIS_URL_ENV_VAR)
DB_HOSTNAME = os.getenv(DB_HOSTNAME_ENV_VAR)
print(f"{PROD=}")
print(f"{REDIS_URL}")
print(f"{dotenv_path=}")

r = redis.Redis().from_url(REDIS_URL, decode_responses=True)

con = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    host=DB_HOSTNAME,
    )
# TODO: commenting this must create either a memory leak or a hanging DB connection
#   however, it was somehow getting called on checkmate, which ended up
#   a) interrupting the front end such that the checkmate isn't indicated in the UI and
#   b) preventing the game from being saved to the DB
# atexit.register(lambda: con.close())


def create_completed_games_table() -> None:
    q = ("create table games ("
            "uid varchar, "
            "moves varchar, "
            "half_moves integer, "
            "white_can_castle_kingside integer, "
            "black_can_castle_queenside integer, "
            "black_can_castle_kingside integer, "
            "white_can_castle_queenside integer, "
            "turn integer, "
            "half_moves_since_last_capture integer, "
            "en_passant_square varchar, "
            "its_check integer, "
            "checkmate integer, "
            "stalemate integer, "
            "abandoned integer, "
            "resigned integer, "
            "draw integer, "
            "winner integer"
        ")"
    )
    pprint(q)
    with con:
        with con.cursor() as cur:
            cur.execute(q)


def truncate_completed_games_table() -> None:
    with con:
        with con.cursor() as cur:
            cur.execute("delete from games")
