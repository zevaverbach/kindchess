import zevchess.ztypes as t


def test_get_possible_moves_rook():
    board = t.Board.from_FEN(t.STARTING_FEN)
    rook = board.a1
    assert rook is not None
    assert isinstance(rook, t.Rook)
    assert rook.get_possible_moves(board) == []


def test_get_possible_moves_rook2():
    board = t.Board.from_FEN("rnbqkbnr/pppppppp/8/8/8/P7/1PPPPPPP/RNBQKBNR")
    rook = board.a1
    assert rook is not None
    assert isinstance(rook, t.Rook)
    assert rook.get_possible_moves(board) == [t.Move(piece="R", src="a1", dest="a2")]


def test_get_possible_moves_rook_pinned():
    board = t.Board.from_FEN("rnb1kbnr/pppppppp/4q3/P7/2P5/4R3/PPP2PPP/1NBQKBNR")
    rook = board.e3
    assert rook is not None
    assert isinstance(rook, t.Rook)
    possible_moves = rook.get_possible_moves(board)
    assert len(possible_moves) == 4
    for pm in [
        t.Move(piece="R", src="e3", dest="e6", capture=True),
        t.Move(piece="R", src="e3", dest="e5"),
        t.Move(piece="R", src="e3", dest="e6"),
        t.Move(piece="R", src="e3", dest="e2"),
    ]:
        assert pm in possible_moves


def test_get_possible_moves_rook_black():
    board = t.Board.from_FEN(t.STARTING_FEN)
    rook = board.a8
    assert rook is not None
    assert isinstance(rook, t.Rook)
    assert rook.get_possible_moves(board) == []


def test_get_possible_moves_rook_black_2():
    board = t.Board.from_FEN("rnbqkbn1/pppppppp/8/6r1/8/8/PPPPPPPP/RNBQKBNR")
    rook = board.g5
    assert rook is not None
    assert isinstance(rook, t.Rook)
    expect = [
        t.Move(piece="r", src="g5", dest="g2", capture=True),
        t.Move(piece="r", src="g5", dest="g3"),
        t.Move(piece="r", src="g5", dest="g4"),
        t.Move(piece="r", src="g5", dest="g6"),
        t.Move(piece="r", src="g5", dest="a5"),
        t.Move(piece="r", src="g5", dest="b5"),
        t.Move(piece="r", src="g5", dest="c5"),
        t.Move(piece="r", src="g5", dest="d5"),
        t.Move(piece="r", src="g5", dest="e5"),
        t.Move(piece="r", src="g5", dest="f5"),
        t.Move(piece="r", src="g5", dest="h5"),
    ]
    possible_moves = rook.get_possible_moves(board)
    assert len(possible_moves) == len(expect)
    for e in expect:
        assert e in possible_moves
