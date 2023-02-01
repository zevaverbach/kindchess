import zevchess.ztypes as t


def test_get_possible_moves_pawn():
    board = t.Board.from_FEN(t.STARTING_FEN)
    pawn = board.d2
    assert pawn is not None
    assert isinstance(pawn, t.Pawn)
    assert pawn.get_possible_moves(board) == [
        t.Move(piece="P", src="d2", dest="d3"),
        t.Move(piece="P", src="d2", dest="d4"),
    ]


def test_get_possible_moves_pawn2():
    board = t.Board.from_FEN("rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR")
    pawn = board.e4
    assert pawn is not None
    assert isinstance(pawn, t.Pawn)
    assert pawn.get_possible_moves(board) == [
        t.Move(piece="P", src="e4", dest="e5"),
        t.Move(piece="P", src="e4", dest="d5", capture=True),
    ]


def test_get_possible_moves_pawn_en_passant():
    board = t.Board.from_FEN("rnbqkbnr/ppp1pppp/8/2Pp4/8/8/PP1PPPPP/RNBQKBNR")
    pawn = board.c5
    assert pawn is not None
    assert isinstance(pawn, t.Pawn)
    assert pawn.get_possible_moves(board, en_passant_square="d5") == [
        t.Move(piece="P", src="c5", dest="c6"),
        t.Move(piece="P", src="c5", dest="d6", capture=True),
    ]


def test_get_possible_moves_pawn_pinned():
    board = t.Board.from_FEN("rnb1kbnr/ppppqppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR")
    pawn = board.e4
    assert pawn is not None
    assert isinstance(pawn, t.Pawn)
    assert pawn.get_possible_moves(board) == [
        t.Move(piece="P", src="e4", dest="e5"),
        t.Move(piece="P", src="e4", dest="d5", capture=True),
    ]


def test_get_possible_moves_pawn_black():
    board = t.Board.from_FEN(t.STARTING_FEN)
    pawn = board.d7
    assert pawn is not None
    assert isinstance(pawn, t.Pawn)
    assert pawn.get_possible_moves(board) == [
        t.Move(piece="p", src="d7", dest="d6"),
        t.Move(piece="p", src="d7", dest="d5"),
    ]
