import copy
import dataclasses as dc
import sqlite3
import string
import typing
from uuid import uuid4

from rich.pretty import pprint

from zevchess.db import r
import zevchess.queries as q
import zevchess.ztypes as t


class InvalidArguments(Exception):
    pass


class NotYourTurn(Exception):
    pass


class InvalidState(Exception):
    pass


EXISTING_UIDS = "existing_uids"
TURN = "turn"
NUM_MOVES = "num_moves"
BLANK = "BLANK"


def create_game() -> str:
    uid = None
    while uid is None or r.lpos(name=EXISTING_UIDS, value=uid):
        uid = str(uuid4())
    r.hset(uid, mapping=dc.asdict(t.GameState()))  # type: ignore
    update_existing_uids_cache(uid)
    return uid


def validate_move_arg(move, turn: int) -> None:
    print(f"{move=}")
    if move.castle:
        if any(
            i is not None for i in (move.piece, move.src, move.dest)
        ):
            raise InvalidArguments
        return
    if any(
        i is None for i in (move.piece, move.src, move.dest)
    ):
        raise InvalidArguments
    if (turn and move.piece.isupper()) or (not turn and move.piece.islower()):
        raise NotYourTurn


def delete_game_from_redis(uid: str) -> None:
    # delete moves
    r.delete(f"game-{uid}")
    # delete state
    r.delete(uid)
    print(f"deleting {uid} from existing_uids")
    r.lrem("existing_uids", 1, uid)


class Checkmate(Exception):
    pass


class Stalemate(Exception):
    pass


class NoPendingPawnPromotion(Exception):
    pass


def choose_promotion_piece(
    uid: str,
    piece_type: typing.Literal["r", "q", "n", "b"],
    state: t.GameState | None = None,
    testing: bool = False,
) -> t.GameState:
    state = state or q.get_game_state(uid)
    if state.need_to_choose_pawn_promotion_piece == "":
        raise NoPendingPawnPromotion
    src, dest, capture_str = state.need_to_choose_pawn_promotion_piece.split(" ")
    capture = int(capture_str)
    piece = piece_type if state.turn else piece_type.upper()
    move = t.Move(piece, src=src, dest=dest, capture=capture)
    return make_move_and_persist(
        uid, move, pawn_promotion=piece, testing=testing, state=state
    )


class InvalidMove(Exception):
    pass


def make_move_and_persist(
    uid: str,
    move: t.Move,
    pawn_promotion: str = "",
    state: t.GameState | None = None,
    testing: bool = False,
) -> t.GameState:
    """
    could raise
      - Checkmate
      - Stalemate
      - InvalidMove
      - InvalidState
      - InvalidArguments
      - NotYourTurn
    """
    state = state or q.get_game_state(uid)

    # draw offer is implicitly rejected if a move is made by either side
    if state.draw_offered != -1:
        state.draw_offered = -1

    if not pawn_promotion and state.need_to_choose_pawn_promotion_piece:
        raise InvalidState("need to choose promotion piece before doing a new move")

    validate_move_arg(move, state.turn)

    board = t.Board.from_FEN(state.FEN)
    store_move(uid, move, pawn_promotion=pawn_promotion)

    if pawn_promotion:
        state.need_to_choose_pawn_promotion_piece = ""
        # put the new piece where the pawn had been before its promotion
        # TODO: this is really awkward
        state.FEN = recalculate_FEN(
            state, t.Move(piece=pawn_promotion, src=move.src, dest=move.src), board
        )
        board = t.Board.from_FEN(state.FEN)

    all_possible_moves = q.get_all_legal_moves(state, board)

    if move not in all_possible_moves:
        pprint(state)
        pprint(all_possible_moves)
        raise InvalidMove(f"{move=}")

    new_state = get_new_state(state, move, board)
    if new_state.checkmate:
        if not testing:
            save_game_to_db(uid, new_state)
            remove_game_from_cache(uid)
        raise Checkmate(new_state.turn)
    if new_state.stalemate:
        if not testing:
            save_game_to_db(uid, new_state)
            remove_game_from_cache(uid)
        raise Stalemate(new_state.turn)
    store_state(uid, new_state)
    return new_state


def save_game_to_db(uid: str, state: t.GameState) -> None:
    moves = r.lrange(f"game-{uid}", 0, -1)
    store_completed_game(uid, moves, state)


def store_completed_game(uid: str, moves: list[str], state: t.GameState) -> None:
    db_dict = state.to_db_dict()
    db_dict_num_entries = len(db_dict)
    field_names = db_dict.keys()
    query = f"insert into games (uid, moves, {', '.join(field_names)}) values(?,?,{','.join(['?' for _ in range(db_dict_num_entries)])})"
    with sqlite3.connect("completed_games.db") as s:
        try:
            s.execute(query, (uid, " ".join(moves), *db_dict.values()))
        except (sqlite3.ProgrammingError, sqlite3.OperationalError):
            print(query, uid, db_dict.values())
            raise


def remove_game_from_cache(uid: str) -> None:
    delete_game_from_redis(uid)


def accept_draw(uid: str, side: int) -> None:
    state = q.get_game_state(uid)
    if state.draw_offered == -1:
        raise InvalidArguments("there is no draw offered.")
    if state.draw_offered == side:
        raise InvalidArguments(
            "you are the one who requested a draw! you can't accept."
        )
    state.draw = 1
    save_game_to_db(uid, state)
    remove_game_from_cache(uid)


def offer_draw(uid: str, side: int) -> None:
    state = q.get_game_state(uid)
    if state.draw_offered == side:
        raise InvalidArguments("you already have a pending draw request")
    if state.draw_offered == int(not side):
        raise InvalidArguments(
            "your opponent has already offered a draw, accept it if you want"
        )
    state.draw_offered = side
    store_state(uid, state)


def reject_draw(uid: str, side: int) -> None:
    state = q.get_game_state(uid)
    if state.draw_offered == -1:
        raise InvalidArguments("there is no draw offered.")
    if state.draw_offered == side:
        raise InvalidArguments("can't reject your own draw request.")
    state.draw_offered = -1
    store_state(uid, state)


def withdraw_draw(uid: str, side: int) -> None:
    state = q.get_game_state(uid)
    if state.draw_offered == -1:
        raise InvalidArguments("there is no draw offered.")
    if state.draw_offered != side:
        raise InvalidArguments("can't withdraw your opponent's draw request")
    state.draw_offered = -1
    store_state(uid, state)


def is_pawn_promotion(move: t.Move) -> bool:
    if move.piece is None:
        return False
    if move.piece.lower() != "p":  # type: ignore
        return False
    last_rank = 1 if move.piece == "p" else 8
    return int(move.dest[1]) == last_rank  # type: ignore


def get_new_state(state: t.GameState, move: t.Move, board: t.Board) -> t.GameState:
    new_state = copy.deepcopy(state)
    if is_pawn_promotion(move):
        new_state.need_to_choose_pawn_promotion_piece = (
            f"{move.src} {move.dest} {move.capture}"
        )
        return new_state

    if move.capture:
        new_state.half_moves_since_last_capture = 0
    else:
        new_state.half_moves_since_last_capture += 1
    recalculate_en_passant(new_state, move, board)
    new_state.FEN = recalculate_FEN(new_state, move, board)
    new_state.half_moves += 1

    if new_state.half_moves >= 6:
        # first three moves of the game, impossible to castle
        recalculate_castling_state(new_state, move)
        recalculate_king_position(new_state, move)

    new_state.turn = abs(new_state.turn - 1)
    checkmate = q.its_checkmate(new_state)
    stalemate = False
    if not checkmate:
        stalemate = q.its_stalemate(new_state)

    if checkmate:
        new_state.checkmate = 1
        new_state.winner = new_state.turn
    elif stalemate:
        new_state.stalemate = 1

    return new_state


def recalculate_en_passant(state: t.GameState, move: t.Move, board: t.Board) -> None:
    if move.piece is None:
        return
    if move.piece.lower() != "p":  # type: ignore
        return
    file, rank_str = move.src  # type: ignore

    # TODO: is this necessary? it's epxnesive, and might have been accidentally pasted in
    state.FEN = recalculate_FEN(state, move, board)
    dest_f, dest_rank_str = move.dest  # type: ignore
    rank, dest_rank = int(rank_str), int(dest_rank_str)
    if file == dest_f and (dest_rank - rank == 2):
        state.en_passant_square = move.dest  # type: ignore
    elif state.en_passant_square != "":
        state.en_passant_square = ""


def recalculate_king_position(state: t.GameState, move: t.Move) -> None:
    if move.piece is not None and move.piece.lower() == "k":
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


def recalculate_castling_state(state: t.GameState, move: t.Move) -> None:
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


def store_move(uid: str, move: t.Move, pawn_promotion: str = "") -> None:
    # TODO: store moves as a hash maybe?
    if move.castle is not None:
        move_string = "O-o" if move.castle == "k" else "O-o-o"
    elif pawn_promotion:
        up = pawn_promotion.isupper()  # type: ignore
        move_string = f"{'P' if up else 'p'}{move.src}{'x' if move.capture else ''}{move.dest}{pawn_promotion}"
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


def get_updated_FEN_src_rank(fen: str, src_file_idx: int, en_passant: str = "") -> str:
    updated_rank = []
    tokens_src = split_FEN_into_tokens(fen)
    en_passant_idx = -1
    if en_passant:
        en_passant_idx = string.ascii_lowercase.index(en_passant)
    for idx, token in enumerate(tokens_src):
        if idx == src_file_idx:
            updated_rank.append(BLANK)
        else:
            if en_passant and en_passant_idx == idx:
                updated_rank.append(BLANK)
            else:
                updated_rank.append(token)
    return create_FEN_from_tokens(updated_rank)


def get_updated_FEN_dest_rank(fen, dest_file_idx, piece: str) -> str:
    tokens_dest = split_FEN_into_tokens(fen)
    updated_rank = []

    for idx, token in enumerate(tokens_dest):
        if idx == dest_file_idx:
            updated_rank.append(piece)
        else:
            updated_rank.append(token)
    return create_FEN_from_tokens(updated_rank)


def get_updated_FEN_same_rank(
    fen: str, piece: str, src_file_idx: int, dest_file_idx: int
) -> str:
    updated_rank = []
    tokens_src = split_FEN_into_tokens(fen)

    for idx, token in enumerate(tokens_src):
        if idx == dest_file_idx:
            updated_rank.append(piece)
        elif idx == src_file_idx:
            updated_rank.append(BLANK)
        else:
            updated_rank.append(token)
    return create_FEN_from_tokens(updated_rank)


def get_updated_rank_FENs(move, ranks, board) -> dict[int, str]:
    updated_ranks = {}
    src_file_idx = string.ascii_lowercase.index(move.src[0])
    src_rank_idx = int(move.src[1]) - 1
    src_rank_FEN = ranks[src_rank_idx]

    dest_file, dest_rank_string = move.dest  # type: ignore
    dest_file_idx = string.ascii_lowercase.index(dest_file)
    dest_rank_idx = int(dest_rank_string) - 1

    en_passant = ""
    if move.capture and move.piece.lower() == "p" and getattr(board, move.dest) is None:
        en_passant = move.dest[0]

    if dest_rank_idx == src_rank_idx:
        updated_ranks[src_rank_idx] = get_updated_FEN_same_rank(
            fen=src_rank_FEN,
            piece=move.piece,  # type: ignore
            src_file_idx=src_file_idx,
            dest_file_idx=dest_file_idx,
        )
    else:
        dest_rank_FEN = ranks[dest_rank_idx]

        updated_ranks[src_rank_idx] = get_updated_FEN_src_rank(
            fen=src_rank_FEN,
            src_file_idx=src_file_idx,
            en_passant=en_passant,
        )
        updated_ranks[dest_rank_idx] = get_updated_FEN_dest_rank(fen=dest_rank_FEN, dest_file_idx=dest_file_idx, piece=move.piece)  # type: ignore
    return updated_ranks


def recalculate_FEN(state: t.GameState, move: t.Move, board: t.Board) -> str:
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
            move=move, ranks=ranks, board=board
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


def store_state(uid: str, state: t.GameState) -> None:
    r.hset(uid, mapping=dc.asdict(state))  # type: ignore


def update_existing_uids_cache(uid: str | list[str]) -> None:
    if isinstance(uid, list):
        r.lpush("existing_uids", *uid)
    else:
        r.lpush("existing_uids", uid)


def remove_all_active_game_uids_from_redis():
    for i in r.lrange("existing_uids", 0, -1):
        r.lrem("existing_uids", 1, i)
