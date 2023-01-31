import zevchess.ztypes as t


def test_its_check_for_TRUE():
    board = t.Board.from_FEN("rnb1kbnr/ppppqppp/8/8/8/8/PPPP1PPP/RNBQKBNR")
    assert t.its_check_for(side=0, board=board, king_square="e1")


def test_its_check_for_TRUE_knight():
    board = t.Board.from_FEN("rnbqkbnr/pppppppp/5N2/8/8/8/PPPPPPPP/RNBQKB1R")
    assert t.its_check_for(side=1, board=board, king_square="e8")


def test_its_check_for_TRUE_bishop():
    board = t.Board.from_FEN("k1r2bnp/2pppppp/8/1p6/8/6P1/PPPPPPBP/RNBQK1NR")
    assert t.its_check_for(side=1, board=board, king_square="a8")


def test_its_check_for_TRUE_pawn():
    board = t.Board.from_FEN("rnbqkbnr/pp1ppppp/8/8/1P6/8/PPPpPPPP/RNBQKBNR")
    assert t.its_check_for(side=0, board=board, king_square="e1")


def test_its_check_for_FALSE():
    board = t.Board.from_FEN(t.STARTING_FEN)
    assert not t.its_check_for(side=0, board=board, king_square="e1")
    assert not t.its_check_for(side=1, board=board, king_square="e1")


def test_its_check_TRUE_illegal_king_sitch():
    board = t.Board.from_FEN("rnbq1bnr/pppppppp/8/3k4/4K3/8/PPPPPPPP/RNBQ1BNR")
    assert t.its_check_for(side=1, board=board, king_square="d5")
    assert t.its_check_for(side=0, board=board, king_square="e4")
