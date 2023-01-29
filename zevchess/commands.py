import dataclasses as dc
import sqlite3
from uuid import uuid4

import zevchess.validate as v
from zevchess.db import r
import zevchess.queries as q
import zevchess.ztypes as t


class InvalidArguments(Exception):
    pass


EXISTING_UIDS = "existing_uids"
TURN = "turn"
NUM_MOVES = "num_moves"


def create_game() -> t.Uid:
    uid = None
    while uid is None or r.sismember(name=EXISTING_UIDS, value=uid):
        uid = str(uuid4())
    r.hset(uid, mapping=dc.asdict(t.GameState())) # type: ignore
    return t.Uid(uid)


def make_move(uid: t.Uid, move: t.Move) -> None:
    if move.castle is None and any(
        i is None for i in (move.piece, move.src, move.dest)
    ):
        raise InvalidArguments

    state = q.get_game_state(uid)
    v.validate_move(uid, move, state)
    store_move(uid, move)

    state = get_new_state(state, move)
    store_state(state)
    raise NotImplementedError


def get_new_state(state: t.GameState, move: t.Move) -> t.GameState:
    if state.half_moves == 0:
        # first move of the game, impossible to capture
        state.half_moves_since_last_capture = 1
    elif move.capture:
        state.half_moves_since_last_capture = 0
    else:
        state.half_moves_since_last_capture += 1
    recalculate_castling_state(state, move)
    recalculate_FEN(state.FEN, move)
    state.half_moves += 1
    state.turn = int(not state.turn)

    return state


def recalculate_castling_state(state: t.GameState, move: t.Move) -> None:
    if (
        state.turn == 0 
        and (state.black_can_castle_queenside or state.black_can_castle_kingside) 
        and (move.castle is not None or 
            (move.piece is not None and move.piece in "kr")
        )
    ):
        if move.castle is not None:
            state.black_can_castle_kingside = 0
            state.black_can_castle_queenside = 0
        elif move.piece == "k":
            state.black_can_castle_kingside = 0
            state.black_can_castle_queenside = 0
        elif move.src == "a8":
            state.black_can_castle_kingside = 0
        elif move.src == "h8":
            state.black_can_castle_queenside = 0
    elif (
        state.turn == 1
        and (state.white_can_castle_queenside or state.white_can_castle_kingside) 
        and (move.castle is not None or 
            (move.piece is not None and move.piece in "kr")
        )
    ):
        if move.castle is not None:
            state.white_can_castle_kingside = 0
            state.white_can_castle_queenside = 0
        elif move.piece == "k":
            state.white_can_castle_kingside = 0
            state.white_can_castle_queenside = 0
        elif move.src == "a1":
            state.white_can_castle_kingside = 0
        elif move.src == "h1":
            state.white_can_castle_queenside = 0



def store_move(uid: t.Uid, move: t.Move) -> None:
    if move.castle is not None:
        move_string = "O-o" if move.castle == "k" else "O-o-o"
    else:
        move_string = f"{move.piece}{move.src}{'x' if move.capture else ''}{move.dest}"

    r.lpush(f"game-{uid}", move_string)


def recalculate_FEN(fen: t.FEN, move: t.Move) -> None:
    raise NotImplementedError


def store_state(uid: t.Uid, state: t.GameState) -> None:
    r.hset(uid, mapping=dc.asdict(state)) # type: ignore


def store_completed_game(uid: t.Uid, moves: list[str]) -> None:
    with sqlite3.connect("completed_games.db") as s:
        s.execute("insert into games (uid, moves) values(?,?)", (uid, " ".join(moves)))
    update_existing_uids_cache(uid)


def update_existing_uids_cache(uid: t.Uid | list[t.Uid]) -> None:
    if isinstance(uid, list):
        r.sadd("existing_uids", *uid)
    else:
        r.sadd("existing_uids", uid)
