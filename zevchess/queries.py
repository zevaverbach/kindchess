import dataclasses as dc
import sqlite3

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
