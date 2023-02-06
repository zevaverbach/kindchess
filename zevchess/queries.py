import sqlite3

from rich.pretty import pprint

from zevchess.db import r
from zevchess.print_board import print_board_from_FEN
import zevchess.ztypes as t


def get_existing_uids_from_db() -> list[str]:
    with sqlite3.connect("completed_games.db") as s:
        c = s.execute("select uid from games")
        return c.fetchall()


def get_game_state(uid: str) -> t.GameState:
    state_dict = r.hgetall(uid)
    return t.GameState.from_redis(state_dict)  # type: ignore


def uid_exists_and_is_an_active_game(uid: str) -> bool:
    return r.hmget(uid, "turn") != [None]


def get_all_legal_moves(
    state: t.GameState, board: t.Board | None = None
) -> list[t.Move]:
    board = board or t.Board.from_FEN(state.FEN)
    if state.turn:
        pieces = board.black_pieces()
        king_square = state.king_square_black
        K = "k"
    else:
        pieces = board.white_pieces()
        king_square = state.king_square_white
        K = "K"

    return [
        move
        for piece in pieces
        for move in piece.get_possible_moves(board, state.en_passant_square)
        if not t.it_would_be_self_check(piece, move, board, king_square if move.piece != K else move.dest)  # type: ignore
    ] + get_castling_moves(state, board)


def its_checkmate(state: t.GameState) -> bool:
    board = t.Board.from_FEN(state.FEN)
    if not t.its_check_for(
        # TODO: why does this make the `test_make_move_its_checkmate` test fail??
        # int(not state.turn),
        state.turn,
        board,
        state.king_square_black if state.turn else state.king_square_white,
    ):
        return False
    return get_all_legal_moves(state, board) == []


def its_stalemate(state: t.GameState) -> bool:
    board = t.Board.from_FEN(state.FEN)
    if t.its_check_for(
        state.turn,
        board,
        state.king_square_black if state.turn else state.king_square_white,
    ):
        return False
    all_possible_moves = get_all_legal_moves(state, board)
    return all_possible_moves == []


def get_castling_moves(state: t.GameState, board: t.Board) -> list[t.Move]:
    moves = []
    if state.turn:
        king = board.e8
        if (
            state.black_can_castle_kingside
            and king is not None
            and isinstance(king, t.King)
            and board.f8 is None
            and board.g8 is None
            and not any(
                t.it_would_be_self_check(
                    piece=king,  # type: ignore
                    move=t.Move(piece="k", src="e8", dest=dest),
                    board=board,
                    king_square="e8",
                )
                for dest in ("f8", "g8")
            )
        ):
            moves.append(t.Move(castle="k"))
        if (
            state.black_can_castle_queenside
            and king is not None
            and isinstance(king, t.King)
            and board.b8 is None
            and board.c8 is None
            and board.d8 is None
            and not any(
                t.it_would_be_self_check(
                    piece=king,  # type: ignore
                    move=t.Move(piece="k", src="e8", dest=dest),
                    board=board,
                    king_square="e8",
                )
                for dest in ("b8", "c8", "d8")
            )
        ):
            moves.append(t.Move(castle="q"))
        return moves
    king = board.e1
    if (
        state.black_can_castle_kingside
        and king is not None
        and isinstance(king, t.King)
        and board.f1 is None
        and board.g1 is None
        and not any(
            t.it_would_be_self_check(
                piece=king,  # type: ignore
                move=t.Move(piece="k", src="e1", dest=dest),
                board=board,
                king_square=dest,
            )
            for dest in ("f1", "g1")
        )
    ):
        moves.append(t.Move(castle="k"))
    if (
        state.black_can_castle_queenside
        and king is not None
        and isinstance(king, t.King)
        and board.b1 is None
        and board.c1 is None
        and board.d1 is None
        and not any(
            t.it_would_be_self_check(
                piece=king,  # type: ignore
                move=t.Move(piece="k", src="e1", dest=dest),
                board=board,
                king_square=dest,
            )
            for dest in ("b1", "c1", "d1")
        )
    ):
        moves.append(t.Move(castle="q"))
    return moves
