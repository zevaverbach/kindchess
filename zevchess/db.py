import sqlite3

import redis

r = redis.Redis(decode_responses=True)
COMPLETED_GAMES = "completed_games.db"


def create_completed_games_table() -> None:
    with sqlite3.connect(COMPLETED_GAMES) as s:
        s.execute(
            "create table games ("
            "uid string, "
            "moves string, "
            "half_moves integer, "
            "white_can_castle_kingside integer, "
            "black_can_castle_queenside integer, "
            "black_can_castle_kingside integer, "
            "white_can_castle_queenside integer, "
            "turn integer, "
            "half_moves_since_last_capture integer, "
            "en_passant_square string, "
            "checkmate integer, "
            "stalemate integer, "
            "abandoned integer"
            ")"
        )


def truncate_completed_games_table() -> None:
    with sqlite3.connect(COMPLETED_GAMES) as s:
        s.execute("delete from games")
