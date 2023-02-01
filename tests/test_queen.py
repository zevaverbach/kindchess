import zevchess.ztypes as t


def test_get_possible_moves_queen():
    board = t.Board.from_FEN(t.STARTING_FEN)
    queen = board.d1
    assert queen is not None
    assert isinstance(queen, t.Queen)
    assert queen.get_possible_moves(board) == []


def test_get_possible_moves_queen2():
    board = t.Board.from_FEN("rnbqkbnr/pppppppp/8/8/8/3P4/PPP1PPPP/RNBQKBNR")
    queen = board.d1
    assert queen is not None
    assert isinstance(queen, t.Queen)
    assert queen.get_possible_moves(board) == [t.Move(piece="Q", src="d1", dest="d2")]


def test_get_possible_moves_queen_black():
    board = t.Board.from_FEN("rnb1kbnr/pppppppp/8/8/2P2q2/4P3/PPP1P1PP/RNBQKBNR")
    queen = board.f4
    assert queen is not None
    assert isinstance(queen, t.Queen)
    expect = [
        t.Move(piece="q", src="f4", dest="d4"),
        t.Move(piece="q", src="f4", dest="e4"),
        t.Move(piece="q", src="f4", dest="g4"),
        t.Move(piece="q", src="f4", dest="h4"),
        t.Move(piece="q", src="f4", dest="c4", capture=True),
        t.Move(piece="q", src="f4", dest="f1", capture=True),
        t.Move(piece="q", src="f4", dest="f2"),
        t.Move(piece="q", src="f4", dest="f3"),
        t.Move(piece="q", src="f4", dest="f5"),
        t.Move(piece="q", src="f4", dest="f6"),
        t.Move(piece="q", src="f4", dest="e3", capture=True),
        t.Move(piece="q", src="f4", dest="g5"),
        t.Move(piece="q", src="f4", dest="h6"),
        t.Move(piece="q", src="f4", dest="h2", capture=True),
        t.Move(piece="q", src="f4", dest="g3"),
        t.Move(piece="q", src="f4", dest="e5"),
        t.Move(piece="q", src="f4", dest="d6"),
    ]
    possible_moves = queen.get_possible_moves(board)
    for e in expect:
        assert e in possible_moves
    assert len(possible_moves) == len(expect)
