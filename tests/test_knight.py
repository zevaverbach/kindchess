import zevchess.ztypes as t


def test_knight_free_reign():
    board = t.Board.from_FEN("rnbqkbnr/pppppppp/8/8/4N3/8/PPP1P1PP/RNBQKB1R")
    knight = board.e4
    assert knight is not None
    assert isinstance(knight, t.Knight)
    expect = [
        t.Move(piece="N", src="e4", dest="c5"),
        t.Move(piece="N", src="e4", dest="c3"),
        t.Move(piece="N", src="e4", dest="g5"),
        t.Move(piece="N", src="e4", dest="g3"),
        t.Move(piece="N", src="e4", dest="d2"),
        t.Move(piece="N", src="e4", dest="f2"),
        t.Move(piece="N", src="e4", dest="d6"),
        t.Move(piece="N", src="e4", dest="f6"),
    ]
    possible_moves = knight.get_possible_moves(board)
    assert len(possible_moves) == len(expect)
    for e in expect:
        assert e in possible_moves
