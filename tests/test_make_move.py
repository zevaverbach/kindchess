import pytest

from zevchess import commands as c
from zevchess import queries as q
from zevchess import ztypes as t


def test_make_move_en_passant():
    state = t.GameState(
        FEN="8/8/1K6/3pP3/8/8/5k2/8",
        half_moves=20,
        en_passant_square="d5",
        king_square_white="b6",
        king_square_black="f2",
    )
    board = t.Board.from_FEN(state.FEN)
    move = t.Move(piece="P", src="e5", dest="d6", capture=1)
    new_state = c.get_new_state(state, move, board)
    new_board = t.Board.from_FEN(new_state.FEN)
    assert new_state.en_passant_square == ""
    assert new_board.d6 == t.Pawn(color=False, square="d6")
    assert new_board.d5 is None


def test_make_move_its_checkmate():
    state = t.GameState(
        FEN="r2qkbnr/p1pppQpp/8/8/2Q5/8/P1PPPPPP/RNB1KBNR",
        half_moves=20,
        king_square_white="e1",
        king_square_black="e8",
        turn=1,
    )
    assert q.its_checkmate(state, t.Board.from_FEN(state.FEN))


def test_make_move_its_stalemate():
    state = t.GameState(
        FEN="7k/5Q2/6K1/8/8/8/8/8",
        half_moves=20,
        king_square_white="e1",
        king_square_black="h8",
        turn=1,
    )
    assert q.its_stalemate(state, t.Board.from_FEN(state.FEN))


def test_pawn_promotion_with_capture():
    state = t.GameState(
        FEN="r2qkbnr/pPpppppp/8/8/8/8/P1PPPPPP/RNBQKBNR",
        half_moves=20,
        king_square_white="e1",
        king_square_black="e8",
        turn=0,
    )
    move = t.Move(piece="P", src="b7", dest="a8", capture=1)
    board = t.Board.from_FEN(state.FEN)
    new_state = c.get_new_state(state, move, board)
    assert new_state.turn == state.turn
    assert new_state.need_to_choose_pawn_promotion_piece
    assert (
        new_state.need_to_choose_pawn_promotion_piece
        == f"{move.src} {move.dest} {move.capture}"
    )
    assert new_state.half_moves == 20
    assert new_state.FEN == state.FEN


def test_pawn_promotion_no_capture():
    state = t.GameState(
        FEN="r2qkbnr/pPpppppp/8/8/8/8/P1PPPPPP/RNBQKBNR",
        half_moves=20,
        king_square_white="e1",
        king_square_black="e8",
        turn=0,
    )
    move = t.Move(piece="P", src="b7", dest="b8")
    board = t.Board.from_FEN(state.FEN)
    new_state = c.get_new_state(state, move, board)
    assert new_state.turn == state.turn
    assert new_state.need_to_choose_pawn_promotion_piece
    assert (
        new_state.need_to_choose_pawn_promotion_piece
        == f"{move.src} {move.dest} {move.capture}"
    )
    assert new_state.half_moves == 20
    assert new_state.FEN == state.FEN


def test_after_pawn_promotion_piece_is_chosen():
    state = t.GameState(
        FEN="r2qkbnr/pPpppppp/8/8/8/8/P1PPPPPP/RNBQKBNR",
        half_moves=20,
        king_square_white="e1",
        king_square_black="e8",
        turn=0,
    )
    move = t.Move(piece="P", src="b7", dest="b8")
    board = t.Board.from_FEN(state.FEN)
    new_state = c.get_new_state(state, move, board)
    newer_state = c.choose_promotion_piece(
        uid="hi", piece_type="q", state=new_state, testing=True
    )
    assert newer_state.FEN == "rQ1qkbnr/p1pppppp/8/8/8/8/P1PPPPPP/RNBQKBNR"
    assert not newer_state.need_to_choose_pawn_promotion_piece


def test_before_pawn_promotion_piece_is_chosen():
    state = t.GameState(
        FEN="r2qkbnr/pPpppppp/8/8/8/8/P1PPPPPP/RNBQKBNR",
        half_moves=20,
        king_square_white="e1",
        king_square_black="e8",
        turn=0,
        need_to_choose_pawn_promotion_piece="yes",
    )
    move = t.Move(piece="P", src="c2", dest="c3")
    with pytest.raises(c.InvalidState):
        c.make_move_and_persist(uid="hi", move=move, state=state)


def test_before_draw_offer_is_addressed():
    """
    If you move when someone has offered a draw, the draw is automatically rejected and the move is accepted.
    """
    state = t.GameState(FEN=t.STARTING_FEN, draw_offered=1)
    move = t.Move(piece="P", src="c2", dest="c3")
    # doesn't raise InvalidState
    new_state = c.make_move_and_persist(uid="hi", move=move, state=state)
    assert new_state.draw_offered == -1


def test_make_move_for_specific_bug_2():
    state = t.GameState(
        FEN="rnbqkbnr/ppppp2p/5p2/6p1/3P4/4P3/PPP2PPP/RNBQKBNR",
        king_square_white="e1",
        king_square_black="e8",
        half_moves=6,
        turn=0,
    )
    with pytest.raises(c.Checkmate):
        c.make_move_and_persist(
            uid="hi",
            state=state,
            move=t.Move(piece="Q", src="d1", dest="h5", capture=0, castle=None),
            testing=True,
        )


def test_get_new_state_for_specific_bug_2():
    fen = "rnbqkbnr/ppppp2p/5p2/6p1/3P4/4P3/PPP2PPP/RNBQKBNR"
    state = t.GameState(
        FEN=fen,
        king_square_white="e1",
        king_square_black="e8",
        half_moves=6,
        turn=0,
    )
    move = t.Move(piece="Q", src="d1", dest="h5", capture=0, castle=None)
    new_state = c.get_new_state(state, move, t.Board.from_FEN(fen))
    assert new_state.FEN == "rnbqkbnr/ppppp2p/5p2/6pQ/3P4/4P3/PPP2PPP/RNB1KBNR"
    assert new_state.checkmate == 1
    assert new_state.turn == 1
    assert new_state.king_square_white == "e1"
    assert new_state.king_square_black == "e8"
    assert new_state.half_moves == 7
    assert new_state.black_can_castle_kingside == 1
    assert new_state.white_can_castle_kingside == 1
    assert new_state.black_can_castle_queenside == 1
    assert new_state.white_can_castle_queenside == 1
    assert new_state.half_moves_since_last_capture == 1
    assert new_state.en_passant_square == ""
    assert new_state.need_to_choose_pawn_promotion_piece == ""
    assert new_state.stalemate == 0


def test_get_new_state_for_specific_bug_3():
    """
    This rook turns from black to white mysteriously
    """
    fen = "1nbqkbnr/1pQpppp1/r7/7p/8/4P3/PPPP1PPP/RNB1KBNR"
    state = t.GameState(
        half_moves=7,
        black_can_castle_kingside=1,
        white_can_castle_kingside=1,
        black_can_castle_queenside=1,
        white_can_castle_queenside=1,
        turn=1,
        half_moves_since_last_capture=0,
        king_square_white="e1",
        king_square_black="e8",
        en_passant_square="",
        need_to_choose_pawn_promotion_piece="",
        checkmate=0,
        stalemate=0,
        abandoned=0,
        FEN=fen,
    )
    move = t.Move(**{"src": "a6", "dest": "h6", "piece": "r"})
    new_state = c.get_new_state(state, move, t.Board.from_FEN(fen))
    assert new_state.FEN == "1nbqkbnr/1pQpppp1/7r/7p/8/4P3/PPPP1PPP/RNB1KBNR"


def test_state_after_move_for_specific_bug_2():
    state = t.GameState(
        FEN="rnbqkbnr/ppppp2p/5p2/6pQ/3P4/4P3/PPP2PPP/RNB1KBNR",
        turn=1,
        king_square_white="e1",
        king_square_black="e8",
    )
    assert q.its_checkmate(state, t.Board.from_FEN(state.FEN))


def test_state_after_move_for_specific_bug_5():
    """fastest possible mate"""
    state = t.GameState(
        FEN="rnb1kbnr/pppp1ppp/4p3/8/5PPq/8/PPPPP2P/RNBQKBNR",
        turn=0,
        king_square_white="e1",
        king_square_black="e8",
    )
    assert q.its_checkmate(state, t.Board.from_FEN(state.FEN))


def test_after_move_for_specific_bug_2_more_state():
    state = t.GameState(
        half_moves=7,
        black_can_castle_kingside=1,
        white_can_castle_kingside=1,
        black_can_castle_queenside=1,
        white_can_castle_queenside=1,
        turn=1,
        half_moves_since_last_capture=1,
        king_square_white="e1",
        king_square_black="e8",
        en_passant_square="",
        need_to_choose_pawn_promotion_piece="",
        checkmate=0,
        stalemate=0,
        FEN="rnbqkbnr/ppppp2p/5p2/6pQ/3P4/4P3/PPP2PPP/RNB1KBNR",
    )
    assert q.its_checkmate(state, t.Board.from_FEN(state.FEN))


def test_stalemate_bug_4():
    """
    from 'the fastest stalemate', in ten moves
    """
    state = t.GameState(
        half_moves=19,
        king_square_white="e1",
        king_square_black="g6",
        turn=1,
        FEN="5bnr/4p1pq/4Qpkr/7p/7P/4P3/PPPP1PP1/RNB1KBNR",
    )
    assert q.its_stalemate(state, t.Board.from_FEN(state.FEN))


def test_stalemate_bug_4_make_move():
    fen = "2Q2bnr/4p1pq/5pkr/7p/7P/4P3/PPPP1PP1/RNB1KBNR"
    state = t.GameState(
        king_square_white="e1",
        king_square_black="g6",
        turn=0,
        FEN="5bnr/4p1pq/4Qpkr/7p/7P/4P3/PPPP1PP1/RNB1KBNR",
    )
    move = t.Move(**{"src": "c8", "dest": "e6", "piece": "Q"})
    new_state = c.get_new_state(state, move, t.Board.from_FEN(fen))
    assert new_state.FEN == "5bnr/4p1pq/4Qpkr/7p/7P/4P3/PPPP1PP1/RNB1KBNR"
    assert new_state.stalemate == 1


def test_make_move_bug_9():
    fen = "2kr3r/p2pQ2p/1p2p3/8/5b2/P7/1N3PPP/4K2R"
    state = t.GameState(
        king_square_white="e1",
        king_square_black="c8",
        turn=0,
        half_moves=8,
        FEN=fen,
    )
    move = t.Move(castle="k")
    new_state = c.get_new_state(state, move, t.Board.from_FEN(fen))
    assert new_state.FEN == "2kr3r/p2pQ2p/1p2p3/8/5b2/P7/1N3PPP/5RK1"
    assert new_state.white_can_castle_kingside == 0
    assert new_state.white_can_castle_queenside == 0


def test_make_move_bug_10():
    state = t.GameState(
        king_square_white="g1",
        king_square_black="g8",
        turn=0,
        FEN="r1b3k1/ppp1Q1pp/8/1B2ppP1/3P4/5PP1/PPP4P/RNB2RK1",
        black_can_castle_kingside=0,
        black_can_castle_queenside=0,
        white_can_castle_kingside=0,
        white_can_castle_queenside=0,
        half_moves=20,
    )
    move = t.Move(**{"src": "e7", "dest": "e8", "piece": "Q"})
    new_state = c.get_new_state(state, move, t.Board.from_FEN(state.FEN))
    assert new_state.checkmate == 1


def test_make_move_bug_11():
    """
    After castling it seems like we don't know where the king is.
    """
    state = t.GameState(
        king_square_white="g1",
        king_square_black="e8",
        turn=1,
        FEN="r1b1k2r/ppp3pp/8/4ppP1/3P4/2QB1PP1/PPP4P/RNB2RK1",
        black_can_castle_kingside=1,
        black_can_castle_queenside=1,
        white_can_castle_kingside=0,
        white_can_castle_queenside=0,
        half_moves=20,
    )
    new_state = state
    for move in [
        t.Move(castle="k"),
        t.Move(**{"src": "c3", "dest": "a3", "piece": "Q"}),
        t.Move(**{"src": "f8", "dest": "f6", "piece": "r"}),
        t.Move(**{"src": "a3", "dest": "a4", "piece": "Q"}),
        t.Move(**{"src": "f6", "dest": "g6", "piece": "r"}),
    ]:
        new_state = c.get_new_state(new_state, move, t.Board.from_FEN(state.FEN))
    move = t.Move(**{"src": "a4", "dest": "e8", "piece": "Q"})
    new_state = c.get_new_state(new_state, move, t.Board.from_FEN(state.FEN))
    assert new_state.checkmate == 1


def test_make_move_bug_6():
    state = t.GameState(
        king_square_white="g1",
        king_square_black="c8",
        turn=0,
        FEN="2kr4/p2p4/1p2p2p/6r1/6b1/P2Q4/1N3PPP/5RK1",
    )
    move = t.Move(**{"src": "d3", "dest": "c3", "piece": "Q"})
    new_state = c.get_new_state(state, move, t.Board.from_FEN(state.FEN))
    assert new_state.check == 1


def test_state_after_move_for_bug_6():
    state = t.GameState(
        FEN="2kr4/p2p4/1p2p2p/8/8/P7/1N2bPrP/5RK1",
        turn=0,
        king_square_white="g1",
        king_square_black="c8",
    )
    assert q.its_check(state, t.Board.from_FEN(state.FEN))


def test_state_after_move_for_bug_7():
    state = t.GameState(
        FEN="2kr4/p2p4/1p2p2p/6r1/2Q3b1/P7/1N3PPP/5RK1",
        turn=1,
        king_square_white="g1",
        king_square_black="c8",
    )
    assert q.its_check(state, t.Board.from_FEN(state.FEN))


def test_state_after_move_for_bug_12():
    state = t.GameState(
        FEN="rnbqkbnr/p3pppp/8/1B1p4/4P3/1p3N2/P1PP1PPP/RNBQ1RK1",
        turn=1,
        king_square_white="g1",
        king_square_black="e8",
    )
    assert q.its_check(state, t.Board.from_FEN(state.FEN))


def test_make_move_bug_12():
    state = t.GameState(
        king_square_white="g1",
        king_square_black="e8",
        turn=0,
        FEN="rnbqkbnr/p3pppp/8/3p4/4P3/1p3N2/P1PPBPPP/RNBQ1RK1",
    )
    move = t.Move(**{"src": "e2", "dest": "b5", "piece": "B"})
    new_state = c.get_new_state(state, move, t.Board.from_FEN(state.FEN))
    assert new_state.check == 1


def test_make_move_and_persist_bug_12():
    state = t.GameState(
        king_square_white="g1",
        king_square_black="e8",
        turn=0,
        FEN="rnbqkbnr/p3pppp/8/3p4/4P3/1p3N2/P1PPBPPP/RNBQ1RK1",
    )
    move = t.Move(**{"src": "e2", "dest": "b5", "piece": "B"})
    new_state = c.make_move_and_persist(uid="hi", move=move, state=state)
    assert new_state.check == 1


def test_make_move_and_persist_bug_13():
    state = t.GameState(
        half_moves=10,
        king_square_white="f1",
        king_square_black="c8",
        turn=1,
        FEN="2k4N/ppp5/5n1p/8/4N2n/8/PPbb2r1/5K2",
    )
    move = t.Move(src="c2", dest="d3", piece="b")
    with pytest.raises(c.Checkmate):
        c.make_move_and_persist(uid="hi", move=move, state=state)
