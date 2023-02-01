import zevchess.queries as q
import zevchess.ztypes as t


def test_get_all_legal_moves_STARTING_white():
    state = t.GameState()
    expect = [
        t.Move(piece="P", src="a2", dest="a3"),
        t.Move(piece="P", src="b2", dest="b3"),
        t.Move(piece="P", src="c2", dest="c3"),
        t.Move(piece="P", src="d2", dest="d3"),
        t.Move(piece="P", src="e2", dest="e3"),
        t.Move(piece="P", src="f2", dest="f3"),
        t.Move(piece="P", src="g2", dest="g3"),
        t.Move(piece="P", src="h2", dest="h3"),
        t.Move(piece="P", src="a2", dest="a4"),
        t.Move(piece="P", src="b2", dest="b4"),
        t.Move(piece="P", src="c2", dest="c4"),
        t.Move(piece="P", src="d2", dest="d4"),
        t.Move(piece="P", src="e2", dest="e4"),
        t.Move(piece="P", src="f2", dest="f4"),
        t.Move(piece="P", src="g2", dest="g4"),
        t.Move(piece="P", src="h2", dest="h4"),
        t.Move(piece="N", src="b1", dest="c3"),
        t.Move(piece="N", src="b1", dest="a3"),
        t.Move(piece="N", src="g1", dest="h3"),
        t.Move(piece="N", src="g1", dest="f3"),
    ]
    got = q.get_all_legal_moves(state)
    for e in expect:
        assert e in got
    assert len(got) == len(expect)


def test_get_moves_includes_castling():
    state = t.GameState(FEN="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQK2R")
    expect = [
        t.Move(piece="P", src="a2", dest="a3"),
        t.Move(piece="P", src="b2", dest="b3"),
        t.Move(piece="P", src="c2", dest="c3"),
        t.Move(piece="P", src="d2", dest="d3"),
        t.Move(piece="P", src="e2", dest="e3"),
        t.Move(piece="P", src="f2", dest="f3"),
        t.Move(piece="P", src="g2", dest="g3"),
        t.Move(piece="P", src="h2", dest="h3"),
        t.Move(piece="P", src="a2", dest="a4"),
        t.Move(piece="P", src="b2", dest="b4"),
        t.Move(piece="P", src="c2", dest="c4"),
        t.Move(piece="P", src="d2", dest="d4"),
        t.Move(piece="P", src="e2", dest="e4"),
        t.Move(piece="P", src="f2", dest="f4"),
        t.Move(piece="P", src="g2", dest="g4"),
        t.Move(piece="P", src="h2", dest="h4"),
        t.Move(piece="N", src="b1", dest="c3"),
        t.Move(piece="N", src="b1", dest="a3"),
        t.Move(piece="K", src="e1", dest="f1"),
        t.Move(piece="R", src="h1", dest="f1"),
        t.Move(piece="R", src="h1", dest="g1"),
        t.Move(castle="k"),
    ]
    got = q.get_all_legal_moves(state)
    for e in expect:
        assert e in got
    assert len(got) == len(expect)


def test_get_moves_castling_is_blocked():
    state = t.GameState(FEN="rnbqk1nr/pppppppp/8/2b5/8/5P2/PPPPP1PP/RNBQK2R")
    expect = [
        t.Move(piece="P", src="a2", dest="a3"),
        t.Move(piece="P", src="b2", dest="b3"),
        t.Move(piece="P", src="c2", dest="c3"),
        t.Move(piece="P", src="d2", dest="d3"),
        t.Move(piece="P", src="e2", dest="e3"),
        t.Move(piece="P", src="g2", dest="g3"),
        t.Move(piece="P", src="h2", dest="h3"),
        t.Move(piece="P", src="a2", dest="a4"),
        t.Move(piece="P", src="b2", dest="b4"),
        t.Move(piece="P", src="c2", dest="c4"),
        t.Move(piece="P", src="d2", dest="d4"),
        t.Move(piece="P", src="e2", dest="e4"),
        t.Move(piece="P", src="f3", dest="f4"),
        t.Move(piece="P", src="g2", dest="g4"),
        t.Move(piece="P", src="h2", dest="h4"),
        t.Move(piece="N", src="b1", dest="c3"),
        t.Move(piece="N", src="b1", dest="a3"),
        t.Move(piece="K", src="e1", dest="f1"),
        t.Move(piece="K", src="e1", dest="f2"),
        t.Move(piece="R", src="h1", dest="f1"),
        t.Move(piece="R", src="h1", dest="g1"),
    ]
    got = q.get_all_legal_moves(state)
    for e in expect:
        assert e in got
    if len(got) > len(expect):
        for g in got:
            assert g in expect
    assert len(got) == len(expect)


def test_get_moves_castling_is_blocked_by_a_knight():
    state = t.GameState(FEN="rnbqkb1r/pppppppp/8/8/8/5Pn1/PPPPP1PP/RNBQK2R")
    expect = [
        t.Move(piece="P", src="a2", dest="a3"),
        t.Move(piece="P", src="b2", dest="b3"),
        t.Move(piece="P", src="c2", dest="c3"),
        t.Move(piece="P", src="d2", dest="d3"),
        t.Move(piece="P", src="e2", dest="e3"),
        t.Move(piece="P", src="h2", dest="h3"),
        t.Move(piece="P", src="a2", dest="a4"),
        t.Move(piece="P", src="b2", dest="b4"),
        t.Move(piece="P", src="c2", dest="c4"),
        t.Move(piece="P", src="d2", dest="d4"),
        t.Move(piece="P", src="e2", dest="e4"),
        t.Move(piece="P", src="f3", dest="f4"),
        t.Move(piece="P", src="h2", dest="h4"),
        t.Move(piece="P", src="h2", dest="g3", capture=True),
        t.Move(piece="N", src="b1", dest="c3"),
        t.Move(piece="N", src="b1", dest="a3"),
        t.Move(piece="K", src="e1", dest="f1"),
        t.Move(piece="K", src="e1", dest="f2"),
        t.Move(piece="R", src="h1", dest="f1"),
        t.Move(piece="R", src="h1", dest="g1"),
    ]
    got = q.get_all_legal_moves(state)
    for e in expect:
        assert e in got
    if len(got) > len(expect):
        for g in got:
            assert g in expect
    assert len(got) == len(expect)


def test_get_moves_dont_include_castling_because_bishop_in_the_way():
    state = t.GameState(FEN="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKB1R")
    expect = [
        t.Move(piece="P", src="a2", dest="a3"),
        t.Move(piece="P", src="b2", dest="b3"),
        t.Move(piece="P", src="c2", dest="c3"),
        t.Move(piece="P", src="d2", dest="d3"),
        t.Move(piece="P", src="e2", dest="e3"),
        t.Move(piece="P", src="f2", dest="f3"),
        t.Move(piece="P", src="g2", dest="g3"),
        t.Move(piece="P", src="h2", dest="h3"),
        t.Move(piece="P", src="a2", dest="a4"),
        t.Move(piece="P", src="b2", dest="b4"),
        t.Move(piece="P", src="c2", dest="c4"),
        t.Move(piece="P", src="d2", dest="d4"),
        t.Move(piece="P", src="e2", dest="e4"),
        t.Move(piece="P", src="f2", dest="f4"),
        t.Move(piece="P", src="g2", dest="g4"),
        t.Move(piece="P", src="h2", dest="h4"),
        t.Move(piece="N", src="b1", dest="c3"),
        t.Move(piece="N", src="b1", dest="a3"),
        t.Move(piece="R", src="h1", dest="g1"),
    ]
    got = q.get_all_legal_moves(state)
    for e in expect:
        assert e in got
    if len(got) > len(expect):
        for g in got:
            assert g in expect
    assert len(got) == len(expect)


def test_get_moves_includes_castling_both_sides():
    state = t.GameState(FEN="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/R3K2R")
    expect = [
        t.Move(piece="P", src="a2", dest="a3"),
        t.Move(piece="P", src="b2", dest="b3"),
        t.Move(piece="P", src="c2", dest="c3"),
        t.Move(piece="P", src="d2", dest="d3"),
        t.Move(piece="P", src="e2", dest="e3"),
        t.Move(piece="P", src="f2", dest="f3"),
        t.Move(piece="P", src="g2", dest="g3"),
        t.Move(piece="P", src="h2", dest="h3"),
        t.Move(piece="P", src="a2", dest="a4"),
        t.Move(piece="P", src="b2", dest="b4"),
        t.Move(piece="P", src="c2", dest="c4"),
        t.Move(piece="P", src="d2", dest="d4"),
        t.Move(piece="P", src="e2", dest="e4"),
        t.Move(piece="P", src="f2", dest="f4"),
        t.Move(piece="P", src="g2", dest="g4"),
        t.Move(piece="P", src="h2", dest="h4"),
        t.Move(piece="K", src="e1", dest="f1"),
        t.Move(piece="K", src="e1", dest="d1"),
        t.Move(piece="R", src="h1", dest="f1"),
        t.Move(piece="R", src="h1", dest="g1"),
        t.Move(piece="R", src="a1", dest="b1"),
        t.Move(piece="R", src="a1", dest="c1"),
        t.Move(piece="R", src="a1", dest="d1"),
        t.Move(castle="k"),
        t.Move(castle="q"),
    ]
    got = q.get_all_legal_moves(state)
    for e in expect:
        assert e in got
    assert len(got) == len(expect)


def test_get_possible_moves_rook_pinned():
    state = t.GameState(FEN="rnb1kbnr/pppppppp/4q3/P7/2P5/4R3/PPP2PPP/1NBQKBNR")
    expect = [
        t.Move(piece="R", src="e3", dest="e6", capture=True),
        t.Move(piece="R", src="e3", dest="e2"),
        t.Move(piece="R", src="e3", dest="e4"),
        t.Move(piece="R", src="e3", dest="e5"),
    ]
    got = q.get_all_legal_moves(state)
    for e in expect:
        assert e in got
    for dont_expect in [
        t.Move(piece="R", src="e3", dest="a3"),
        t.Move(piece="R", src="e3", dest="b3"),
        t.Move(piece="R", src="e3", dest="c3"),
        t.Move(piece="R", src="e3", dest="d3"),
        t.Move(piece="R", src="e3", dest="f3"),
        t.Move(piece="R", src="e3", dest="g3"),
        t.Move(piece="R", src="e3", dest="h3"),
    ]:
        assert dont_expect not in got


def test_get_possible_moves_queen_pinned():
    state = t.GameState(FEN="rn1qkbnr/pppppppp/8/b7/8/5P2/PPPQ1PPP/RNB1KBNR")
    expect = [
        t.Move(piece="Q", src="d2", dest="c3"),
        t.Move(piece="Q", src="d2", dest="b4"),
        t.Move(piece="Q", src="d2", dest="a5", capture=True),
    ]
    got = q.get_all_legal_moves(state)
    for e in expect:
        assert e in got
    for dont_expect in [
        t.Move(piece="Q", src="d2", dest="d1"),
        t.Move(piece="Q", src="d2", dest="d3"),
        t.Move(piece="Q", src="d2", dest="d4"),
        t.Move(piece="Q", src="d2", dest="d5"),
        t.Move(piece="Q", src="d2", dest="d6"),
    ]:
        assert dont_expect not in got


def test_get_all_legal_moves_including_en_passant():
    state = t.GameState(
        FEN="8/8/1K6/3pP3/8/8/5k2/8",
        en_passant_square="d5",
        king_square_white="b6",
        king_square_black="f2",
    )
    expect = [
        t.Move(piece="P", src="e5", dest="e6"),
        t.Move(piece="P", src="e5", dest="d6", capture=True),
    ]
    got = q.get_all_legal_moves(state)
    for e in expect:
        assert e in got
