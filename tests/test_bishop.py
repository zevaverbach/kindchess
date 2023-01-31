import zevchess.ztypes as t


def test_get_possible_moves_bishop():
    board = t.Board.from_FEN(t.STARTING_FEN)
    bishop = board.c1
    assert bishop is not None
    assert isinstance(bishop, t.Bishop)
    assert bishop.get_possible_moves(board) == []



def test_get_possible_moves_bishop2():
    board = t.Board.from_FEN("rnbqkbnr/pppppppp/8/8/8/3P4/PPP1PPPP/RNBQKBNR")
    bishop = board.c1
    assert bishop is not None
    assert isinstance(bishop, t.Bishop)
    assert bishop.get_possible_moves(board) == [
        t.Move(piece="B", src="c1", dest="d2"),
        t.Move(piece="B", src="c1", dest="e3"),
        t.Move(piece="B", src="c1", dest="f4"),
        t.Move(piece="B", src="c1", dest="g5"),
        t.Move(piece="B", src="c1", dest="h6"),
    ]


def test_get_possible_moves_bishop_3():
    board = t.Board.from_FEN("rnbqkb1r/pppppppp/3n4/8/5B2/8/PPPPPPPP/RN1QKBNR")
    bishop = board.f4
    assert bishop is not None
    assert isinstance(bishop, t.Bishop)
    expect = [
        t.Move(piece="B", src="f4", dest="g3"),
        t.Move(piece="B", src="f4", dest="e5"),
        t.Move(piece="B", src="f4", dest="e3"),
        t.Move(piece="B", src="f4", dest="g5"),
        t.Move(piece="B", src="f4", dest="h6"),
        t.Move(piece="B", src="f4", dest="d6", capture=True),
    ]
    possible_moves = bishop.get_possible_moves(board)
    for e in expect:
        assert e in possible_moves
    assert len(possible_moves) == len(expect)
