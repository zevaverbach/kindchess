from zevchess import commands as c
from zevchess import ztypes as t


def test_make_move_en_passant():
    state = t.GameState(FEN="8/8/1K6/3pP3/8/8/5k2/8", half_moves=20, en_passant_square="d5", king_square_white="b6", king_square_black="f2")
    board = t.Board.from_FEN(state.FEN)
    move = t.Move(piece="P", src="e5", dest="d6", capture=True)
    new_state = c.get_new_state(state, move, board)
    new_board = t.Board.from_FEN(new_state.FEN)
    assert new_state.en_passant_square == ""
    assert new_board.d6 == t.Pawn(color=False, square="d6")
    assert new_board.d5 == None

