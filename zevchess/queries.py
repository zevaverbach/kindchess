import dataclasses as dc
import sqlite3

from zevchess.db import r
import zevchess.ztypes as t


def get_existing_uids_from_db() -> list[t.Uid]:
    with sqlite3.connect("completed_games.db") as s:
        c = s.execute("select uid from games")
        return list(map(lambda game: t.Uid(game), c.fetchall()))


def get_game_state(uid: t.Uid) -> t.GameState:
    fields = [f.name for f in dc.fields(t.GameState)]
    print(fields)
    return t.GameState.from_redis(r.hmget(uid, fields)) # type: ignore


def get_all_legal_moves(state: t.GameState) -> list[t.Move]:
    # TODO
    raise NotImplementedError
