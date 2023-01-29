import sqlite3

import redis

r = redis.Redis()
COMPLETED_GAMES = "completed_games.db"


def create_completed_games_table() -> None:
    with sqlite3.connect(COMPLETED_GAMES) as s:
        s.execute("create table games (uid string, moves string)")


def truncate_completed_games_table() -> None:
    with sqlite3.connect(COMPLETED_GAMES) as s:
        s.execute("delete from games")
