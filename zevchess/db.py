import atexit
import os

from dotenv import load_dotenv
import psycopg2
import redis
from rich.pretty import pprint

PROD = os.getenv("ZEVCHESS_PROD")
dotenv_path = ".env" if PROD else ".env-dev"
load_dotenv(dotenv_path)

REDIS_URL = os.getenv("REDIS_URL") if PROD == 1 else os.getenv("REDIS_URL_PUBLIC")
DB_URL = os.getenv("DB_URL")


r = redis.Redis().from_url(REDIS_URL, decode_responses=True)
con = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    host=os.getenv("DB_HOSTNAME"),
    )
atexit.register(lambda: con.close())


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
