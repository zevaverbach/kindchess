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
