import pytest
from rich.pretty import pprint

from zevchess import commands as c
from zevchess.print_board import print_board_from_FEN
from zevchess import queries as q
from zevchess.ztypes import Move


def test_make_move_and_persist_stalemate_bug_4():
    uid = c.create_game()
    moves = (
        {"src": "f7", "dest": "g6", "piece": "k"},
        {"src": "b8", "dest": "c8", "piece": "Q", "capture": 1},
        {"src": "d3", "dest": "h7", "piece": "q"},
        {"src": "b7", "dest": "b8", "piece": "Q", "capture": 1},
        {"src": "d8", "dest": "d3", "piece": "q"},
        {"src": "d7", "dest": "b7", "piece": "Q", "capture": 1},
        {"src": "e8", "dest": "f7", "piece": "k"},
        {"src": "c7", "dest": "d7", "piece": "Q", "capture": 1},
        {"src": "f7", "dest": "f6", "piece": "p"},
        {"src": "h2", "dest": "h4", "piece": "P"},
        {"src": "a6", "dest": "h6", "piece": "r"},
        {"src": "a5", "dest": "c7", "piece": "Q", "capture": 1},
        {"src": "h7", "dest": "h5", "piece": "p"},
        {"src": "h5", "dest": "a5", "piece": "Q", "capture": 1},
        {"src": "a8", "dest": "a6", "piece": "r"},
        {"src": "d1", "dest": "h5", "piece": "Q"},
        {"src": "a7", "dest": "a5", "piece": "p"},
        {"src": "e2", "dest": "e3", "piece": "P"},
    )
    state = q.get_game_state(uid)
    for move in reversed(moves):
        mov = Move(**move)
        try:
            state = c.make_move_and_persist(uid, state=state, move=mov, testing=True)
        except c.InvalidMove:
            pprint(mov)
            print_board_from_FEN(state.FEN)
    mov = Move(**{"src": "c8", "dest": "e6", "piece": "Q"})
    with pytest.raises(c.Stalemate):
        c.make_move_and_persist(uid, state=state, move=mov, testing=True)


def test_make_move_and_persist_bug_5():
    """fastest possible mate"""
    uid = c.create_game()
    state = q.get_game_state(uid)
    state = c.make_move_and_persist(uid, state=state, move=Move(src="f2", dest="f4", piece="P"))
    state = c.make_move_and_persist(uid, state=state, move=Move(src="e7", dest="e6", piece="p"))
    state = c.make_move_and_persist(uid, state=state, move=Move(src="g2", dest="g4", piece="P"))
    with pytest.raises(c.Checkmate):
        c.make_move_and_persist(uid, state=state, move=Move(src="d8", dest="h4", piece="q"))
