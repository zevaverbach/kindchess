from zevchess.ztypes import Board, STARTING_FEN


def test_board_from_fen():
    board = Board.from_FEN("8/4k3/8/8/3R4/8/5K2/8")
    assert board.e7 == "k"
    assert board.d4 == "R"
    assert board.f2 == "K"


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
