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
        # TODO: these are failing
        t.Move(piece="N", src="b1", dest="c3"),
        t.Move(piece="N", src="b1", dest="a3"),
        t.Move(piece="N", src="g1", dest="h3"),
        t.Move(piece="N", src="g1", dest="f3"),
    ]
    got = q.get_all_legal_moves(state)
    for e in expect:
        assert e in got
    assert len(got) == len(expect)
