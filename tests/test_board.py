import pytest

from zevchess import commands
from zevchess.ztypes import Board, STARTING_FEN


@pytest.mark.skip()
def test_board_from_fen():
    board = Board.from_FEN("8/4k3/8/8/3R4/8/5K2/8")
    assert board.e7 == "k"
    assert board.d4 == "R"
    assert board.f2 == "K"


@pytest.mark.skip()
def test_board_from_fen_starting():
    print(STARTING_FEN)
    board = Board.from_FEN(STARTING_FEN)
    assert board.a1 == "R"
    assert board.b1 == "N"
    assert board.c1 == "B"
    assert board.d1 == "Q"
    assert board.e1 == "K"
    assert board.f1 == "B"
    assert board.g1 == "N"
    assert board.h1 == "R"
    assert board.a2 == "P"
    assert board.b2 == "P"
    assert board.c2 == "P"
    assert board.d2 == "P"
    assert board.e2 == "P"
    assert board.f2 == "P"
    assert board.g2 == "P"
    assert board.h2 == "P"
    assert board.a7 == "p"
    assert board.b7 == "p"
    assert board.c7 == "p"
    assert board.d7 == "p"
    assert board.e7 == "p"
    assert board.f7 == "p"
    assert board.g7 == "p"
    assert board.h7 == "p"
    assert board.a8 == "r"
    assert board.b8 == "n"
    assert board.c8 == "b"
    assert board.d8 == "q"
    assert board.e8 == "k"
    assert board.f8 == "b"
    assert board.g8 == "n"
    assert board.h8 == "r"


def test_get_FEN_from_board():
    board = Board.from_FEN(STARTING_FEN)
    assert commands.get_FEN_from_board(board) == STARTING_FEN

def test_get_FEN_from_board_2():
    BLANK = "8/8/8/8/8/8/8/8"
    board = Board.from_FEN(BLANK)
    assert commands.get_FEN_from_board(board) == BLANK

def test_get_FEN_from_board_3():
    ENDGAME = "8/1k3q2/8/8/8/3K4/8/8"
    board = Board.from_FEN(ENDGAME)
    assert commands.get_FEN_from_board(board) == ENDGAME
