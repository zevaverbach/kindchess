from zevchess.db import r
import zevchess.ztypes as t


class NoSuchGame(Exception):
    pass


def get_active_game_uids() -> list[str]:
    return r.lrange("existing_uids", 0, -1)


def get_game_state(uid: str) -> t.GameState:
    state_dict = get_game_state_dict(uid)
    if not state_dict:
        raise NoSuchGame
    return t.GameState.from_redis(state_dict)  # type: ignore


def get_game_state_dict(uid: str) -> dict:
    return r.hgetall(uid)


def uid_exists_and_is_an_active_game(uid: str) -> bool:
    state = get_game_state_dict(uid)
    print(state)
    return (
        len(state) != 0
        and int(state["winner"]) == -1
        and all(
            int(state[key]) == 0
            for key in ("checkmate", "stalemate", "abandoned", "resigned", "draw")
        )
    )
    # 'checkmate': '0', 'stalemate': '0', 'abandoned': '0', 'resigned': '0', 'draw': '0', 'draw_offered': '-1', 'winner': '-1'


def get_all_legal_moves(
    state: t.GameState,
    board: t.Board | None = None,
    json: bool = False,
) -> list[t.Move]:
    board = board or t.Board.from_FEN(state.FEN)
    if state.turn:
        pieces = board.black_pieces()
        king_square = state.king_square_black
        K = "k"
    else:
        pieces = board.white_pieces()
        king_square = state.king_square_white
        K = "K"

    moves = [
        move
        for piece in pieces
        for move in piece.get_possible_moves(board, state.en_passant_square)
        if not t.it_would_be_self_check(piece, move, board, king_square if move.piece != K else move.dest)  # type: ignore
    ] + get_castling_moves(state, board)
    if json:
        return [m.to_json() for m in moves]
    return moves


def its_checkmate(state: t.GameState) -> bool:
    board = t.Board.from_FEN(state.FEN)
    if not t.its_check_for(
        state.turn,
        board,
        state.king_square_black if state.turn else state.king_square_white,
    ):
        return False
    return get_all_legal_moves(state, board) == []


def its_stalemate(state: t.GameState) -> bool:
    board = t.Board.from_FEN(state.FEN)
    if t.its_check_for(
        state.turn,
        board,
        state.king_square_black if state.turn else state.king_square_white,
    ):
        return False
    all_possible_moves = get_all_legal_moves(state, board)
    return all_possible_moves == []


def get_black_castling_moves(state, board):
    moves = []
    king = board.e8
    if king is None or not isinstance(king, t.King):
        return []
    for attr, spaces, letter in (
        ("black_can_castle_kingside", ("f8", "g8"), "k"),
        ("black_can_castle_queenside", ("b8", "c8", "d8"), "q"),
    ):
        if (
            getattr(state, attr)
            and all(getattr(board, space) is None for space in spaces)
            and not any(
                t.it_would_be_self_check(
                    piece=king,
                    move=t.Move(piece="k", src="e8", dest=dest),
                    board=board,
                    king_square=dest,
                )
                for dest in spaces
            )
        ):
            moves.append(t.Move(castle=letter))
    return moves


def get_white_castling_moves(state, board):
    moves = []
    king = board.e1
    if king is None or not isinstance(king, t.King):
        return []
    for attr, spaces, letter in (
        ("white_can_castle_kingside", ("f1", "g1"), "k"),
        ("white_can_castle_queenside", ("b1", "c1", "d1"), "q"),
    ):
        if (
            getattr(state, attr)
            and all(getattr(board, space) is None for space in spaces)
            and not any(
                t.it_would_be_self_check(
                    piece=king,
                    move=t.Move(piece="k", src="e1", dest=dest),
                    board=board,
                    king_square=dest,
                )
                for dest in spaces
            )
        ):
            moves.append(t.Move(castle=letter))
    return moves


def get_castling_moves(state: t.GameState, board: t.Board) -> list[t.Move]:
    if state.turn:
        return get_black_castling_moves(state, board)
    return get_white_castling_moves(state, board)
