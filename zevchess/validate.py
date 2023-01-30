import zevchess.queries as q
import zevchess.ztypes as t


class InvalidMove(Exception):
    pass


def validate_move(uid: t.Uid, move: t.Move_, state: t.GameState) -> None:
    if move not in q.get_all_legal_moves(state):
        raise InvalidMove
