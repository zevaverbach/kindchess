from __future__ import annotations
import abc
import dataclasses as dc
import string
import typing as t

Uid = t.NewType("Uid", str)
# not really a FEN, just the positions part
FEN = t.NewType("FEN", bytes)

# TODO: use these types for a new serialization implementation?

Side = t.Literal[0, 1]
Castle = t.Literal["k", "q"]
# Piece = t.Literal["q", "k", "b", "n", "r", "p"]
File = t.Literal["a", "b", "c", "d", "e", "f", "g", "h"]
Rank = t.Literal[1, 2, 3, 4, 5, 6, 7, 8]
Square = t.Literal[
    "a1",
    "b1",
    "c1",
    "d1",
    "e1",
    "f1",
    "g1",
    "h1",
    "a2",
    "b2",
    "c2",
    "d2",
    "e2",
    "f2",
    "g2",
    "h2",
    "a3",
    "b3",
    "c3",
    "d3",
    "e3",
    "f3",
    "g3",
    "h3",
    "a4",
    "b4",
    "c4",
    "d4",
    "e4",
    "f4",
    "g4",
    "h4",
    "a5",
    "b5",
    "c5",
    "d5",
    "e5",
    "f5",
    "g5",
    "h5",
    "a6",
    "b6",
    "c6",
    "d6",
    "e6",
    "f6",
    "g6",
    "h6",
    "a7",
    "b7",
    "c7",
    "d7",
    "e7",
    "f7",
    "g7",
    "h7",
    "a8",
    "b8",
    "c8",
    "d8",
    "e8",
    "f8",
    "g8",
    "h8",
]


STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"


@dc.dataclass
class GameState:
    half_moves: int = 0
    black_can_castle_kingside: int = 1
    white_can_castle_kingside: int = 1
    black_can_castle_queenside: int = 1
    white_can_castle_queenside: int = 1
    turn: int = 0
    half_moves_since_last_capture: int = -1
    king_square_white: str = "e1"
    king_square_black: str = "e8"
    en_passant_square: str = ""
    need_to_choose_pawn_promotion_piece: str = "" # f"{src} {target} {capture: int}"
    FEN: str = STARTING_FEN

    @classmethod
    def from_redis(cls, redis_response: list[bytes]):
        rr = redis_response
        return cls(
            int(rr[0]),
            int(rr[1]),
            int(rr[2]),
            int(rr[3]),
            int(rr[4]),
            int(rr[5]),
            int(rr[6]),
            rr[7].decode(),
            rr[8].decode(),
            rr[9].decode(),
            rr[10].decode(),
            rr[11].decode(),
        )


@dc.dataclass
class Move:
    piece: str | None = None
    src: str | None = None
    dest: str | None = None
    capture: int = 0
    castle: t.Literal["k", "q"] | None = None


@dc.dataclass
class Piece:
    color: int
    square: str
    directions: list[str] | None = None

    def move(self, dest: str, capture: int = 0):
        return Move(piece=self.name(), src=self.square, dest=dest, capture=capture)

    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @classmethod
    def make(cls, square: str, char: str):
        maker = None
        match char.lower():
            case "p":
                maker = Pawn
            case "r":
                maker = Rook
            case "b":
                maker = Bishop
            case "n":
                maker = Knight
            case "q":
                maker = Queen
            case "k":
                maker = King
            case _:
                # raise Exception("invalid piece type")
                maker = Pawn
        return maker(color=char.islower(), square=square)

    def get_possible_moves(self, board: Board, _: str = "") -> list[Move]:
        return _get_possible_moves(self, board)


@dc.dataclass
class Board:
    a1: Piece | None = None
    b1: Piece | None = None
    c1: Piece | None = None
    d1: Piece | None = None
    e1: Piece | None = None
    f1: Piece | None = None
    g1: Piece | None = None
    h1: Piece | None = None
    a2: Piece | None = None
    b2: Piece | None = None
    c2: Piece | None = None
    d2: Piece | None = None
    e2: Piece | None = None
    f2: Piece | None = None
    g2: Piece | None = None
    h2: Piece | None = None
    a3: Piece | None = None
    b3: Piece | None = None
    c3: Piece | None = None
    d3: Piece | None = None
    e3: Piece | None = None
    f3: Piece | None = None
    g3: Piece | None = None
    h3: Piece | None = None
    a4: Piece | None = None
    b4: Piece | None = None
    c4: Piece | None = None
    d4: Piece | None = None
    e4: Piece | None = None
    f4: Piece | None = None
    g4: Piece | None = None
    h4: Piece | None = None
    a5: Piece | None = None
    b5: Piece | None = None
    c5: Piece | None = None
    d5: Piece | None = None
    e5: Piece | None = None
    f5: Piece | None = None
    g5: Piece | None = None
    h5: Piece | None = None
    a6: Piece | None = None
    b6: Piece | None = None
    c6: Piece | None = None
    d6: Piece | None = None
    e6: Piece | None = None
    f6: Piece | None = None
    g6: Piece | None = None
    h6: Piece | None = None
    a7: Piece | None = None
    b7: Piece | None = None
    c7: Piece | None = None
    d7: Piece | None = None
    e7: Piece | None = None
    f7: Piece | None = None
    g7: Piece | None = None
    h7: Piece | None = None
    a8: Piece | None = None
    b8: Piece | None = None
    c8: Piece | None = None
    d8: Piece | None = None
    e8: Piece | None = None
    f8: Piece | None = None
    g8: Piece | None = None
    h8: Piece | None = None

    def copy(self):
        return self.from_FEN(self.to_FEN())

    @classmethod
    def from_FEN(cls, fen: str) -> t.Self:
        board_dict = {}
        for rank_idx, rank in enumerate(fen.split("/")):
            rank_num = 8 - rank_idx
            index = 0
            for char in rank:
                if char.isnumeric():
                    index += int(char)
                    continue
                fl = string.ascii_lowercase[index]
                key = f"{fl}{rank_num}"
                piece = Piece.make(char=char, square=key)
                board_dict[key] = piece
                index += 1
        return cls(**board_dict)

    def black_pieces(self):
        return [
            piece
            for piece in self.squares()
            if piece is not None and piece.name().islower()
        ]

    def white_pieces(self):
        return [
            piece
            for piece in self.squares()
            if piece is not None and piece.name().isupper()
        ]

    def squares(self) -> list[Piece | None]:
        return [
            getattr(self, f"{fl}{rank}") for rank in range(1, 9) for fl in "abcdefgh"
        ]

    def square_tups_in_FEN_order(self) -> list[tuple[str, Piece]]:
        return [
            (f"{fl}{rank}", getattr(self, f"{fl}{rank}"))
            for rank in range(8, 0, -1)
            for fl in "abcdefgh"
        ]

    def to_FEN(self) -> str:
        return get_FEN_from_board(self)


def get_FEN_from_board(board: Board) -> str:
    blank_count = 0
    fen = ""
    rank = 8
    for square, piece in board.square_tups_in_FEN_order():
        if int(square[1]) != rank:
            rank = int(square[1])
            if blank_count:
                fen += str(blank_count)
                blank_count = 0
            fen += "/"
        if piece is None:
            blank_count += 1
        else:
            if blank_count:
                fen += str(blank_count)
                blank_count = 0
            fen += piece.name()
    if blank_count:
        fen += str(blank_count)
    return fen


@dc.dataclass
class Pawn(Piece):
    def name(self) -> str:
        if self.color == 0:
            return "P"
        return "p"

    def get_move_one_up(self, fl: str, rank: int, board: Board) -> Move | None:
        if self.color:
            one_square_in_front = f"{fl}{rank - 1}"
        else:
            one_square_in_front = f"{fl}{rank + 1}"
        if no_one_is_there(one_square_in_front, board):
            return self.move(one_square_in_front)

    def get_move_two_up(self, fl: str, rank: int, board: Board) -> Move | None:
        if home_row(self.color, rank):
            if self.color:
                two_squares_in_front = f"{fl}{rank - 2}"
            else:
                two_squares_in_front = f"{fl}{rank + 2}"
            if no_one_is_there(two_squares_in_front, board):
                return self.move(two_squares_in_front)

    def get_possible_moves(
        self, board: Board, en_passant_square: str = ""
    ) -> list[Move]:
        possible_moves = []
        fl, rank_str = self.square
        rank = int(rank_str)

        move_one_up = self.get_move_one_up(fl, rank, board)
        if move_one_up is not None:
            possible_moves.append(move_one_up)
            move_two_up = self.get_move_two_up(fl, rank, board)
            if move_two_up is not None:
                possible_moves.append(move_two_up)

        diag_l = None
        try:
            prev_fl, _ = get_prev_fl(fl, -1)
        except Edge:
            pass
        else:
            diag_l = f"{prev_fl}{rank + 1 if self.color == 0 else rank - 1}"
            if an_opponent_is_there(
                from_piece_perspective=self, square=diag_l, board=board
            ):
                possible_moves.append(self.move(diag_l, capture=1))

        diag_r = None
        try:
            next_fl, _ = get_next_fl(fl, -1)
        except Edge:
            pass
        else:
            diag_r = f"{next_fl}{rank + 1 if self.color == 0 else rank - 1}"
            if an_opponent_is_there(
                from_piece_perspective=self, square=diag_r, board=board
            ):
                possible_moves.append(self.move(diag_r, capture=1))

        if en_passant_square != "":
            file_to_left_of_en_passant_square = None
            file_to_right_of_en_passant_square = None
            fl = en_passant_square[0]
            if not fl.startswith("a"):
                file_to_left_of_en_passant_square = string.ascii_lowercase[
                    string.ascii_lowercase.index(fl) - 1
                ]
            if not fl.startswith("h"):
                file_to_right_of_en_passant_square = string.ascii_lowercase[
                    string.ascii_lowercase.index(fl) + 1
                ]
            rank = 4 if self.color else 5
            rank_behind = 3 if self.color else 6
            behind_en_passant_square = f"{fl}{rank_behind}"
            if (
                file_to_left_of_en_passant_square is not None
                and self.square == f"{file_to_left_of_en_passant_square}{rank}"
            ) or (
                file_to_right_of_en_passant_square is not None
                and self.square == f"{file_to_right_of_en_passant_square}{rank}"
            ):
                possible_moves.append(self.move(behind_en_passant_square, capture=1))

        return possible_moves


def home_row(color: int, rank: int) -> bool:
    return (color == 1 and rank == 7) or (color == 0 and rank == 2)


class Obstacle(Exception):
    pass


class NoMove(Exception):
    pass


class Edge(Exception):
    pass


@dc.dataclass
class Rook(Piece):
    directions = list("lurd")

    def name(self) -> str:
        if self.color == 0:
            return "R"
        return "r"


@dc.dataclass
class Queen(Piece):
    directions = ["l", "ul", "u", "ur", "r", "dr", "d", "dl"]

    def name(self) -> str:
        if self.color == 0:
            return "Q"
        return "q"


@dc.dataclass
class Bishop(Piece):
    directions = ["ul", "ur", "dr", "dl"]

    def name(self) -> str:
        if self.color == 0:
            return "B"
        return "b"


@dc.dataclass
class Knight(Piece):
    def name(self) -> str:
        if self.color == 0:
            return "N"
        return "n"

    def get_possible_moves(self, board: Board, _: str = "") -> list[Move]:
        directions = ["2u1l", "2u1r", "2d1l", "2d1r", "1u2l", "1u2r", "1d2l", "1d2r"]
        moves = []
        for direction in directions:
            try:
                possible_move = self.get_possible_move_in_direction(direction=direction, board=board)  # type: ignore
            except (NoMove, Obstacle, Edge):
                continue
            else:
                moves.append(possible_move)
        return moves

    def get_incr_func(
        self,
        direction: t.Literal[
            "2u1l", "2u1r", "2d1l", "2d1r", "1u2l", "1u2r", "1d2l", "1d2r"
        ],
    ) -> t.Callable[[str, int], tuple[str, int]]:
        match direction:
            case "2u1l":

                def do_2u1l(f: str, rank: int):
                    f, rank = get_prev_fl(f, rank)
                    f, rank = get_up_rank(f, rank)
                    return get_up_rank(f, rank)

                return do_2u1l
            case "2u1r":

                def do_2u1r(f: str, rank: int):
                    f, rank = get_next_fl(f, rank)
                    f, rank = get_up_rank(f, rank)
                    return get_up_rank(f, rank)

                return do_2u1r
            case "2d1l":

                def do_2d1l(f: str, rank: int):
                    f, rank = get_prev_fl(f, rank)
                    f, rank = get_down_rank(f, rank)
                    return get_down_rank(f, rank)

                return do_2d1l
            case "2d1r":

                def do_2d1r(f: str, rank: int):
                    f, rank = get_next_fl(f, rank)
                    f, rank = get_down_rank(f, rank)
                    return get_down_rank(f, rank)

                return do_2d1r
            case "1u2l":

                def do_1u2l(f: str, rank: int):
                    f, rank = get_prev_fl(f, rank)
                    f, rank = get_prev_fl(f, rank)
                    return get_up_rank(f, rank)

                return do_1u2l
            case "1u2r":

                def do_1u2r(f: str, rank: int):
                    f, rank = get_next_fl(f, rank)
                    f, rank = get_next_fl(f, rank)
                    return get_up_rank(f, rank)

                return do_1u2r
            case "1d2l":

                def do_1d2l(f: str, rank: int):
                    f, rank = get_prev_fl(f, rank)
                    f, rank = get_prev_fl(f, rank)
                    return get_down_rank(f, rank)

                return do_1d2l
            case "1d2r":

                def do_1d2r(f: str, rank: int):
                    f, rank = get_next_fl(f, rank)
                    f, rank = get_next_fl(f, rank)
                    return get_down_rank(f, rank)

                return do_1d2r
            case _:
                raise Exception(f"no such direction as {direction}")

    def get_possible_move_in_direction(
        self,
        direction: t.Literal[
            "2u1l", "2u1r", "2d1l", "2d1r", "1u2l", "1u2r", "1d2l", "1d2r"
        ],
        board: Board,
    ) -> Move:
        fl, rank_str = self.square
        rank = int(rank_str)

        func = self.get_incr_func(direction)
        fl, rank = func(fl, rank)
        dest_square = f"{fl}{rank}"

        if an_ally_is_there(self, dest_square, board):
            raise Obstacle
        if an_opponent_is_there(self, dest_square, board):
            return self.move(dest_square, capture=1)
        return self.move(dest_square)


@dc.dataclass
class King(Piece):
    directions = ["l", "ul", "u", "ur", "r", "dr", "d", "dl"]

    def name(self) -> str:
        if self.color == 0:
            return "K"
        return "k"

    def get_possible_moves(self, board: Board, _: str = "") -> list[Move]:
        moves = []
        directions = self.__class__.directions
        for direction in directions:  # type: ignore
            try:
                possible_move = self.get_possible_move_in_direction(direction=direction, board=board)  # type: ignore
            except (NoMove, Obstacle, Edge):
                continue
            else:
                moves.append(possible_move)
        return moves

    def get_possible_move_in_direction(
        self,
        direction: t.Literal["l", "ul", "u", "ur", "r", "dr", "d", "dl"],
        board: Board,
    ) -> Move:
        fl, rank_str = self.square
        rank = int(rank_str)

        fl, rank = get_incr_func(direction)(fl, rank)
        dest_square = f"{fl}{rank}"

        if an_ally_is_there(self, dest_square, board):
            raise Obstacle
        if an_opponent_is_there(self, dest_square, board):
            return self.move(dest_square, capture=1)
        return self.move(dest_square)


def it_would_be_self_check(
    piece: Piece, move: Move, board: Board, king_square: str
) -> bool:
    board_after_move = board.copy()
    setattr(board_after_move, move.src, None)  # type: ignore
    setattr(board_after_move, move.dest, piece)  # type: ignore
    side = piece.color
    its_check = its_check_for(side, board=board_after_move, king_square=king_square)
    return its_check


def its_check_for(side: int, board: Board, king_square: str) -> bool:
    if side:
        opposing_pieces = board.white_pieces()
    else:
        opposing_pieces = board.black_pieces()
    for piece in opposing_pieces:
        for move in piece.get_possible_moves(board):
            if move.dest == king_square:
                return True
    return False


def get_up_rank(_: str, rank: int) -> tuple[str, int]:
    if rank == 8:
        raise Edge
    return _, rank + 1


def get_down_rank(_: str, rank: int) -> tuple[str, int]:
    if rank == 1:
        raise Edge
    return _, rank - 1


def get_prev_fl(f: str, _: int) -> tuple[str, int]:
    if f == "a":
        raise Edge
    idx = string.ascii_lowercase.index(f)
    return string.ascii_lowercase[idx - 1], _


def get_ul(f: str, rank: int) -> tuple[str, int]:
    f, _ = get_prev_fl(f, rank)
    _, rank = get_up_rank(f, rank)
    return f, rank


def get_ur(f: str, rank: int) -> tuple[str, int]:
    f, _ = get_next_fl(f, rank)
    _, rank = get_up_rank(f, rank)
    return f, rank


def get_dr(f: str, rank: int) -> tuple[str, int]:
    f, _ = get_next_fl(f, rank)
    _, rank = get_down_rank(f, rank)
    return f, rank


def get_dl(f: str, rank: int) -> tuple[str, int]:
    f, _ = get_prev_fl(f, rank)
    _, rank = get_down_rank(f, rank)
    return f, rank


def get_next_fl(f: str, _: int) -> tuple[str, int]:
    if f == "h":
        raise Edge
    idx = string.ascii_lowercase.index(f)
    return string.ascii_lowercase[idx + 1], _


def no_one_is_there(square: str, board: Board):
    return getattr(board, square) is None


def an_opponent_is_there(from_piece_perspective: Piece, square: str, board: Board):
    piece = getattr(board, square)
    return piece is not None and piece.color != from_piece_perspective.color


def an_ally_is_there(from_piece_perspective: Piece, square: str, board: Board):
    piece = getattr(board, square)
    return piece is not None and piece.color == from_piece_perspective.color


def get_incr_func(direction: str) -> t.Callable[[str, int], tuple[str, int]]:
    match direction:
        case "l":
            return get_prev_fl
        case "r":
            return get_next_fl
        case "u":
            return get_up_rank
        case "d":
            return get_down_rank
        case "ul":
            return get_ul
        case "ur":
            return get_ur
        case "dl":
            return get_dl
        case "dr":
            return get_dr
        case _:
            raise Exception(f"no such direction as {direction}")


def _get_possible_moves(piece: Piece, board: Board, _: str = "") -> list[Move]:
    moves = []
    directions = piece.__class__.directions
    for direction in directions:  # type: ignore
        moves += _get_possible_moves_in_direction(piece=piece, direction=direction, board=board)  # type: ignore
    return moves


def _get_possible_moves_in_direction(
    piece,
    direction: t.Literal["l", "ul", "u", "ur", "r", "dr", "d", "dl"],
    board: Board,
) -> list[Move]:
    fl, rank_str = piece.square
    rank = int(rank_str)
    incr_func = get_incr_func(direction)
    moves = []
    while True:
        try:
            fl, rank = incr_func(fl, rank)
        except Edge:
            break
        else:
            dest_square = f"{fl}{rank}"

        if an_ally_is_there(piece, dest_square, board):
            break

        if an_opponent_is_there(piece, dest_square, board):
            move = piece.move(dest_square, capture=1)
            moves.append(move)
            break

        move = piece.move(dest_square)
        moves.append(move)
    return moves
