import pytest

import zevchess.ztypes as t


def test_get_possible_moves_queen():
    board = t.Board.from_FEN(t.STARTING_FEN)
    queen = board.d1
    assert queen is not None
    assert t.get_possible_moves(queen, board) == []


def test_get_possible_moves_queen2():
    board = t.Board.from_FEN("rnbqkbnr/pppppppp/8/8/8/3P4/PPP1PPPP/RNBQKBNR")
    queen = board.d1
    assert queen is not None
    assert t.get_possible_moves(queen, board) == [t.Move(piece="R", src="a1", dest="a2")]


@pytest.mark.skip()
def test_get_possible_moves_queen_pinned():
    board = t.Board.from_FEN(...)
    queen = board.e3
    assert queen is not None
    possible_moves = t.get_possible_moves(queen, board)
    assert len(possible_moves) == 4
    for pm in [...]:
        assert pm in possible_moves


def test_get_possible_moves_queen_black():
    board = t.Board.from_FEN(...)
    queen = board.g5
    assert queen is not None
    expect = [...]
    possible_moves = t.get_possible_moves(queen, board)
    assert len(possible_moves) == len(expect)
    for e in expect:
        assert e in possible_moves
