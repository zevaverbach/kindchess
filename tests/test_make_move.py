import pytest

from zevchess import commands as c
from zevchess import queries as q
from zevchess import ztypes as t


def test_make_move_en_passant():
    state = t.GameState(
        FEN="8/8/1K6/3pP3/8/8/5k2/8",
        half_moves=20,
        en_passant_square="d5",
        king_square_white="b6",
        king_square_black="f2",
    )
    board = t.Board.from_FEN(state.FEN)
    move = t.Move(piece="P", src="e5", dest="d6", capture=1)
    new_state, _, _ = c.get_new_state(state, move, board)
    new_board = t.Board.from_FEN(new_state.FEN)
    assert new_state.en_passant_square == ""
    assert new_board.d6 == t.Pawn(color=False, square="d6")
    assert new_board.d5 == None


@pytest.mark.skip()
def test_make_move_its_checkmate():
    state = t.GameState(
        ...
    )
    assert q.its_checkmate(state)


@pytest.mark.skip()
def test_make_move_its_stalemate():
    state = t.GameState(
        ...
    )
    assert q.its_stalemate(state)


def test_pawn_promotion():
    state = t.GameState(
        FEN="r2qkbnr/pPpppppp/8/8/8/8/P1PPPPPP/RNBQKBNR",
        half_moves=20,
        king_square_white="e1",
        king_square_black="e8",
        turn=0,
    )
    move = t.Move(piece="P", src="b7", dest="a8", capture=1)
    board = t.Board.from_FEN(state.FEN)
    new_state, _, _ = c.get_new_state(state, move, board)
    assert new_state.turn == state.turn
    assert new_state.need_to_choose_pawn_promotion_piece
    assert new_state.need_to_choose_pawn_promotion_piece == f"{move.src} {move.dest} {move.capture}"
    assert new_state.half_moves == 20
    assert new_state.FEN == state.FEN


def test_pawn_promotion_2():
    state = t.GameState(
        FEN="r2qkbnr/pPpppppp/8/8/8/8/P1PPPPPP/RNBQKBNR",
        half_moves=20,
        king_square_white="e1",
        king_square_black="e8",
        turn=0,
    )
    move = t.Move(piece="P", src="b7", dest="b8")
    board = t.Board.from_FEN(state.FEN)
    new_state, _, _ = c.get_new_state(state, move, board)
    assert new_state.turn == state.turn
    assert new_state.need_to_choose_pawn_promotion_piece
    assert new_state.need_to_choose_pawn_promotion_piece == f"{move.src} {move.dest} {move.capture}"
    assert new_state.half_moves == 20
    assert new_state.FEN == state.FEN


@pytest.mark.skip()
def test_after_pawn_promotion_piece_is_chosen():
    raise NotImplementedError
