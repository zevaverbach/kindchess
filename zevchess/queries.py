import dataclasses as dc
import sqlite3
import string

from zevchess.db import r
import zevchess.ztypes as t


def get_existing_uids_from_db() -> list[str]:
    with sqlite3.connect("completed_games.db") as s:
        c = s.execute("select uid from games")
        return c.fetchall()


def get_game_state(uid: t.Uid) -> t.GameState:
    fields = [f.name for f in dc.fields(t.GameState)]
    print(fields)
    return t.GameState.from_redis(r.hmget(uid, fields))  # type: ignore


def get_all_legal_moves(state: t.GameState) -> list[t.Move]:
    # move: .piece .src .dest 
    # other moves: .capture .castle

    # is the piece pinned?
    raise NotImplementedError


@dc.dataclass
class Pawn:
    square: str

    def get_possible_moves(self, board: t.Board):
        fl, rank_str = self.square
        rank = int(rank_str)
        one_square_in_front = f"{fl}{rank + 1}"
        two_squares_in_front = f"{fl}{rank + 2}"

        diag_l = None
        prev_fl = get_prev_fl(fl)
        if prev_fl is not None:
            diag_l = f"{prev_fl}{rank + 1}"

        diag_r = None
        next_fl = get_next_fl(fl)
        if next_fl is not None:
            diag_l = f"{next_fl}{rank + 1}"


def would_it_be_illegal_because_check(move: t.Move) -> bool:
    raise NotImplementedError
        

def get_prev_fl(f: str) -> str | None:
    if f == "a":
        return None
    idx = string.ascii_lowercase.index(f)
    return string.ascii_lowercase[idx - 1]


def get_next_fl(f: str) -> str | None:
    if f == "h":
        return None
    idx = string.ascii_lowercase.index(f)
    return string.ascii_lowercase[idx + 1]
