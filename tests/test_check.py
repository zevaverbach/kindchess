import zevchess.ztypes as t


def test_its_check_for_TRUE():
    board = t.Board.from_FEN("rnb1kbnr/ppppqppp/8/8/8/8/PPPP1PPP/RNBQKBNR")
    assert t.its_check_for(side=0, board=board, king_square="e1")

def test_its_check_for_FALSE():
    board = t.Board.from_FEN(t.STARTING_FEN)
    assert not t.its_check_for(side=0, board=board, king_square="e1")
    assert not t.its_check_for(side=1, board=board, king_square="e1")
