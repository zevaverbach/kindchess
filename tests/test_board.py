import zevchess.ztypes as t



def test_board_from_fen():
    board = t.Board.from_FEN("8/4k3/8/8/3R4/8/5K2/8")
    assert board.e7.name() == "k"
    assert board.d4.name() == "R"
    assert board.f2.name() == "K"


def test_board_from_fen_starting():
    print(t.STARTING_FEN)
    board = t.Board.from_FEN(t.STARTING_FEN)
    assert board.a1.name() == "R"
    assert board.b1.name() == "N"
    assert board.c1.name() == "B"
    assert board.d1.name() == "Q"
    assert board.e1.name() == "K"
    assert board.f1.name() == "B"
    assert board.g1.name() == "N"
    assert board.h1.name() == "R"
    assert board.a2.name() == "P"
    assert board.b2.name() == "P"
    assert board.c2.name() == "P"
    assert board.d2.name() == "P"
    assert board.e2.name() == "P"
    assert board.f2.name() == "P"
    assert board.g2.name() == "P"
    assert board.h2.name() == "P"
    assert board.a7.name() == "p"
    assert board.b7.name() == "p"
    assert board.c7.name() == "p"
    assert board.d7.name() == "p"
    assert board.e7.name() == "p"
    assert board.f7.name() == "p"
    assert board.g7.name() == "p"
    assert board.h7.name() == "p"
    assert board.a8.name() == "r"
    assert board.b8.name() == "n"
    assert board.c8.name() == "b"
    assert board.d8.name() == "q"
    assert board.e8.name() == "k"
    assert board.f8.name() == "b"
    assert board.g8.name() == "n"
    assert board.h8.name() == "r"


def test_get_FEN_from_board():
    board = t.Board.from_FEN(t.STARTING_FEN)
    assert t.get_FEN_from_board(board) == t.STARTING_FEN


def test_get_FEN_from_board_2():
    BLANK = "8/8/8/8/8/8/8/8"
    board = t.Board.from_FEN(BLANK)
    assert t.get_FEN_from_board(board) == BLANK


def test_get_FEN_from_board_3():
    ENDGAME = "8/1k3q2/8/8/8/3K4/8/8"
    board = t.Board.from_FEN(ENDGAME)
    assert t.get_FEN_from_board(board) == ENDGAME
