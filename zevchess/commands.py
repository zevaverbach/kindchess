import dataclasses as dc
import sqlite3
import string
import typing
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
BLANK = "BLANK"


def create_game() -> t.Uid:
    uid = None
    while uid is None or r.sismember(name=EXISTING_UIDS, value=uid):
        uid = str(uuid4())
    r.hset(uid, mapping=dc.asdict(t.GameState()))  # type: ignore
    return t.Uid(uid)


def make_move(uid: t.Uid, move: t.Move_) -> None:
    if move.castle is None and any(
        i is None for i in (move.piece, move.src, move.dest)
    ):
        raise InvalidArguments

    state = q.get_game_state(uid)
    v.validate_move(uid, move, state)
    store_move(uid, move)

    state = get_new_state(state, move)
    store_state(uid, state)


def get_new_state(state: t.GameState, move: t.Move_) -> t.GameState:
    if state.half_moves == 0:
        # first move of the game, impossible to capture
        state.half_moves_since_last_capture = 1
    elif move.capture:
        state.half_moves_since_last_capture = 0
    else:
        state.half_moves_since_last_capture += 1
    recalculate_castling_state(state, move)
    recalculate_king_position(state, move)
    state.FEN = recalculate_FEN(state, move)
    state.half_moves += 1
    state.turn = int(not state.turn)

    return state


def recalculate_king_position(state: t.GameState, move: t.Move_) -> None:
    if move.piece == "k":
        if state.turn:
            state.king_square_black = move.dest  # type: ignore
        else:
            state.king_square_white = move.dest  # type: ignore
    elif move.castle:
        if state.turn:
            if move.castle == "k":
                state.king_square_black = "g8"
            else:
                state.king_square_black = "c8"
        else:
            if move.castle == "k":
                state.king_square_black = "g1"
            else:
                state.king_square_black = "c1"


def recalculate_castling_state(state: t.GameState, move: t.Move_) -> None:
    if move.piece and move.piece not in "kr":
        return

    if state.turn == 0:
        attr_q = "white_can_castle_queenside"
        attr_k = "white_can_castle_kingside"
        king_rook_origin = "h1"
        queen_rook_origin = "a1"
    else:
        attr_q = "black_can_castle_queenside"
        attr_k = "black_can_castle_kingside"
        king_rook_origin = "h8"
        queen_rook_origin = "a8"

    if getattr(state, attr_q, 0) and getattr(state, attr_k, 0):
        return

    def cant_castle_anymore(side: typing.Literal["k", "q", "both"]) -> None:
        if side in ("k", "both"):
            setattr(state, attr_k, 0)
        if side in ("q", "both"):
            setattr(state, attr_q, 0)

    if move.castle or move.piece == "k":
        cant_castle_anymore("both")
    elif move.src == king_rook_origin:
        cant_castle_anymore("k")
    elif move.src == queen_rook_origin:
        cant_castle_anymore("q")


def store_move(uid: t.Uid, move: t.Move_) -> None:
    if move.castle is not None:
        move_string = "O-o" if move.castle == "k" else "O-o-o"
    else:
        move_string = f"{move.piece}{move.src}{'x' if move.capture else ''}{move.dest}"

    r.lpush(f"game-{uid}", move_string)


def split_FEN_into_tokens(fen: str) -> list[str]:
    tokens = []
    for char in fen:
        if char.isnumeric():
            for _ in range(int(char)):
                tokens.append(BLANK)
        else:
            tokens.append(char)
    return tokens


def create_FEN_from_tokens(tokens: list[str]) -> str:
    FEN = ""
    num_blanks = 0
    for tok in tokens:
        if tok == BLANK:
            num_blanks += 1
            continue
        if num_blanks > 0:
            FEN += str(num_blanks)
            num_blanks = 0
        FEN += tok
    if num_blanks > 0:
        FEN += str(num_blanks)
    return FEN


def get_updated_rank_FEN_after_castling(
    state: t.GameState, castle_side: t.Castle, ranks: list[str]
) -> tuple[int, str]:
    rank_src_idx = 0 if state.turn == 0 else 7
    rank_src_FEN = ranks[rank_src_idx]
    if castle_side == "q":
        LEFT_SIDE_FEN_AFTER_QUEEN_CASTLE = "2kr1" if state.turn == 1 else "2KR1"
        LEFT_SIDE_TOKENS_AFTER_QUEEN_CASTLE = split_FEN_into_tokens(
            LEFT_SIDE_FEN_AFTER_QUEEN_CASTLE
        )
        right_side = split_FEN_into_tokens(rank_src_FEN[3:])  # "2kr(*****)"
        return rank_src_idx, create_FEN_from_tokens(
            LEFT_SIDE_TOKENS_AFTER_QUEEN_CASTLE + right_side
        )

    RIGHT_SIDE_FEN_AFTER_KING_CASTLE = "1rk1" if state.turn == 1 else "1RK1"
    RIGHT_SIDE_TOKENS_AFTER_KING_CASTLE = split_FEN_into_tokens(
        RIGHT_SIDE_FEN_AFTER_KING_CASTLE
    )
    left_side = split_FEN_into_tokens(rank_src_FEN[:4])  # "(****)1rk"
    return rank_src_idx, create_FEN_from_tokens(
        left_side + RIGHT_SIDE_TOKENS_AFTER_KING_CASTLE
    )


def get_updated_FEN_src_rank(fen: str, src_file_idx: int) -> str:
    updated_rank = []
    tokens_src = split_FEN_into_tokens(fen)
    for idx, token in enumerate(tokens_src):
        if idx == src_file_idx:
            updated_rank.append(BLANK)
        else:
            updated_rank.append(token)
    return create_FEN_from_tokens(updated_rank)


def get_updated_FEN_dest_rank(fen, dest_file_idx, turn: int, piece: str) -> str:
    tokens_dest = split_FEN_into_tokens(fen)
    updated_rank = []

    for idx, token in enumerate(tokens_dest):
        if idx == dest_file_idx:
            updated_rank.append(piece if turn == 1 else piece.upper())  # type: ignore
        else:
            updated_rank.append(token)
    return create_FEN_from_tokens(updated_rank)


def get_updated_FEN_same_rank(
    fen: str, turn: int, piece: str, src_file_idx: int, dest_file_idx: int
) -> str:
    updated_rank = []
    tokens_src = split_FEN_into_tokens(fen)

    for idx, token in enumerate(tokens_src):
        if idx == dest_file_idx:
            updated_rank.append(piece if turn == 1 else piece.upper())
        elif idx == src_file_idx:
            updated_rank.append(BLANK)
        else:
            updated_rank.append(token)
    return create_FEN_from_tokens(updated_rank)


def get_updated_rank_FENs(state, move, ranks) -> dict[int, str]:
    updated_ranks = {}
    src_file_idx = string.ascii_lowercase.index(move.src[0])
    src_rank_idx = int(move.src[1]) - 1
    src_rank_FEN = ranks[src_rank_idx]

    dest_file, dest_rank_string = move.dest  # type: ignore
    dest_file_idx = string.ascii_lowercase.index(dest_file)
    dest_rank_idx = int(dest_rank_string) - 1

    if dest_rank_idx == src_rank_idx:
        updated_ranks[src_rank_idx] = get_updated_FEN_same_rank(
            fen=src_rank_FEN,
            turn=state.turn,
            piece=move.piece,  # type: ignore
            src_file_idx=src_file_idx,
            dest_file_idx=dest_file_idx,
        )
    else:
        dest_rank_FEN = ranks[dest_rank_idx]

        updated_ranks[src_rank_idx] = get_updated_FEN_src_rank(
            fen=src_rank_FEN, src_file_idx=src_file_idx
        )
        updated_ranks[dest_rank_idx] = get_updated_FEN_dest_rank(fen=dest_rank_FEN, dest_file_idx=dest_file_idx, turn=state.turn, piece=move.piece)  # type: ignore
    return updated_ranks


def recalculate_FEN(state: t.GameState, move: t.Move_) -> str:
    # TODO: replace this with `do_move(move)` and `board.to_FEN()`
    updated_ranks = {}
    ranks = state.FEN.split("/")[::-1]
    if move.castle is not None:
        rank_src_idx, updated_rank = get_updated_rank_FEN_after_castling(
            state=state, castle_side=move.castle, ranks=ranks
        )
        updated_ranks[rank_src_idx] = updated_rank
    else:
        for rank_idx, updated_FEN in get_updated_rank_FENs(
            move=move, state=state, ranks=ranks
        ).items():
            updated_ranks[rank_idx] = updated_FEN

    updated_FEN = ""
    for i in range(7, -1, -1):
        if i in updated_ranks:
            section = updated_ranks[i]
        else:
            section = ranks[i]
        updated_FEN += section
        if i > 0:
            updated_FEN += "/"
    return updated_FEN


def store_state(uid: t.Uid, state: t.GameState) -> None:
    r.hset(uid, mapping=dc.asdict(state))  # type: ignore


def store_completed_game(uid: t.Uid, moves: list[str]) -> None:
    with sqlite3.connect("completed_games.db") as s:
        s.execute("insert into games (uid, moves) values(?,?)", (uid, " ".join(moves)))
    update_existing_uids_cache(uid)


def update_existing_uids_cache(uid: str | list[str]) -> None:
    if isinstance(uid, list):
        r.sadd("existing_uids", *uid)
    else:
        r.sadd("existing_uids", uid)
