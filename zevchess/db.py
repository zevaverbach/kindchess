import os
import sys

from dotenv import load_dotenv
import psycopg2
import redis
from rich.pretty import pprint

ENVIRONMENT = os.getenv("KINDCHESS_ENVIRONMENT")
if ENVIRONMENT is None:
    print("KINDCHESS_ENVIRONMENT not set")
    sys.exit(1)

match ENVIRONMENT:
    case "local":
        dotenv_path = ".env-local"
        REDIS_URL_ENV_VAR = "REDIS_URL"
        DB_HOSTNAME_ENV_VAR = "DB_HOSTNAME"
    case "prod":
        dotenv_path = ".env"
        REDIS_URL_ENV_VAR = "REDIS_URL"
        DB_HOSTNAME_ENV_VAR = "DB_HOSTNAME"
    case _:
        raise Exception

load_dotenv(dotenv_path, override=True)
REDIS_URL = os.getenv(REDIS_URL_ENV_VAR)
DB_HOSTNAME = os.getenv(DB_HOSTNAME_ENV_VAR)

gotta_exit = False

if REDIS_URL is None:
    print("REDIS_URL not set")
    gotta_exit = True
else:
    r = redis.Redis().from_url(REDIS_URL, decode_responses=True)

if DB_HOSTNAME is None:
    print("DB_HOSTNAME not set")
    gotta_exit = True

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

if DB_NAME is None:
    print("DB_NAME not set")
    gotta_exit = True

if DB_USER is None:
    print("DB_USER not set")
    gotta_exit = True

if DB_PASS is None:
    print("DB_PASS not set")
    gotta_exit = True

if gotta_exit:
    sys.exit(1)


def get_con():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOSTNAME,
    )

def create_completed_games_table() -> None:
    q = (
        "create table games ("
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
    with get_con() as con:
        with con.cursor() as cur:
            cur.execute(q)


def truncate_completed_games_table() -> None:
    with get_con() as con:
        with con.cursor() as cur:
            cur.execute("delete from games")
