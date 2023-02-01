import zevchess.ztypes as t
import zevchess.print_board as pb


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


def test_its_check_when_rook_leaves_pin_1():
    fen = "rnb1kbnr/pppppppp/4q3/P7/2P5/4R3/PPP2PPP/1NBQKBNR"
    orig_board = t.Board.from_FEN(fen)
    king_square = "e1"
    for e in [
        t.Move(piece="R", src="e3", dest="a3"),
        t.Move(piece="R", src="e3", dest="b3"),
        t.Move(piece="R", src="e3", dest="c3"),
        t.Move(piece="R", src="e3", dest="d3"),
        t.Move(piece="R", src="e3", dest="f3"),
        t.Move(piece="R", src="e3", dest="g3"),
        t.Move(piece="R", src="e3", dest="h3"),
    ]:
        board = orig_board.copy()
        setattr(board, e.src, None) # type: ignore
        setattr(board, e.dest, t.Rook(0, e.dest)) # type: ignore
        if not t.its_check_for(0, board, king_square):
            pb.print_board_from_FEN(fen)
        assert t.its_check_for(0, board, king_square)
