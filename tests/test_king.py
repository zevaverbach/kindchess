import pytest

import zevchess.ztypes as t


def test_get_possible_moves_king():
    board = t.Board.from_FEN(t.STARTING_FEN)
    king = board.e1
    assert king is not None
    assert isinstance(king, t.King)
    assert king.get_possible_moves(board) == []


def test_get_possible_moves_king2():
    board = t.Board.from_FEN("rnbqkbnr/pppppppp/8/8/8/3P4/PPP1PPPP/RNBQKBNR")
    king = board.e1
    assert king is not None
    assert isinstance(king, t.King)
    assert king.get_possible_moves(board) == [t.Move(piece="K", src="e1", dest="d2")]


@pytest.mark.skip()
def test_get_possible_moves_king_pinned():
    board = t.Board.from_FEN("rn1qkbnr/pppppppp/8/b7/8/5P2/PPPQ1PPP/RNB1KBNR")
    king = board.d3
    assert king is not None
    assert isinstance(king, t.King)
    possible_moves = king.get_possible_moves(board)
    assert len(possible_moves) == 3
    for pm in [
        t.Move(piece="K", src="d3", dest="c3"),
        t.Move(piece="K", src="d3", dest="b4"),
        t.Move(piece="K", src="d3", dest="a5", capture=True),
    ]:
        assert pm in possible_moves


def test_get_possible_moves_king_black():
    board = t.Board.from_FEN("rnb1kbnr/pppppppp/8/8/2P2q2/4P3/PPP1P1PP/RNBQKBNR")
    king = board.f4
    assert king is not None
    assert isinstance(king, t.King)
    expect = [
        t.Move(piece="k", src="f4", dest="d4"),
    ]
    possible_moves = king.get_possible_moves(board)
    for e in expect:
        assert e in possible_moves
    assert len(possible_moves) == len(expect)
