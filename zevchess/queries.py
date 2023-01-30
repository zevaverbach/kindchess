import abc
import dataclasses as dc
import sqlite3
import string
import typing

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
    board = t.Board.from_FEN(state.FEN)
    if state.turn:
        pieces = board.black_pieces()
    else:
        pieces = board.white_pieces()

    return [
        move
        for piece in pieces
        for move in piece.get_possible_moves()
        if not would_be_illegal_because_check(move, board)
    ]


def would_be_illegal_because_check(move: t.Move, board: t.Board) -> bool:
    # is the piece pinned?
    raise NotImplementedError


