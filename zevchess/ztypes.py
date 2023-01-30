import dataclasses as dc
import string
import typing as t

Uid = t.NewType("Uid", str)
# not really a FEN, just the positions part
FEN = t.NewType("FEN", bytes)

Side = t.Literal[0, 1]
Castle = t.Literal["k", "q"]
Piece = t.Literal["q", "k", "b", "n", "r", "p"]
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


@dc.dataclass
class Move:
    uid: Uid
    piece: Piece | None = None
    src: Square | None = None
    dest: Square | None = None
    capture: bool = False
    castle: Castle | None = None


STARTING_FEN = FEN(b"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")


@dc.dataclass
class GameState:
    half_moves: int = 0
    black_can_castle_kingside: int = 1
    white_can_castle_kingside: int = 1
    black_can_castle_queenside: int = 1
    white_can_castle_queenside: int = 1
    turn: int = 0
    half_moves_since_last_capture: int = -1
    FEN: FEN = STARTING_FEN

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
            FEN(rr[7]),
        )



@dc.dataclass
class Board:
    a1: str | None = None
    b1: str | None = None
    c1: str | None = None
    d1: str | None = None
    e1: str | None = None
    f1: str | None = None
    g1: str | None = None
    h1: str | None = None
    a2: str | None = None
    b2: str | None = None
    c2: str | None = None
    d2: str | None = None
    e2: str | None = None
    f2: str | None = None
    g2: str | None = None
    h2: str | None = None
    a3: str | None = None
    b3: str | None = None
    c3: str | None = None
    d3: str | None = None
    e3: str | None = None
    f3: str | None = None
    g3: str | None = None
    h3: str | None = None
    a4: str | None = None
    b4: str | None = None
    c4: str | None = None
    d4: str | None = None
    e4: str | None = None
    f4: str | None = None
    g4: str | None = None
    h4: str | None = None
    a5: str | None = None
    b5: str | None = None
    c5: str | None = None
    d5: str | None = None
    e5: str | None = None
    f5: str | None = None
    g5: str | None = None
    h5: str | None = None
    a6: str | None = None
    b6: str | None = None
    c6: str | None = None
    d6: str | None = None
    e6: str | None = None
    f6: str | None = None
    g6: str | None = None
    h6: str | None = None
    a7: str | None = None
    b7: str | None = None
    c7: str | None = None
    d7: str | None = None
    e7: str | None = None
    f7: str | None = None
    g7: str | None = None
    h7: str | None = None
    a8: str | None = None
    b8: str | None = None
    c8: str | None = None
    d8: str | None = None
    e8: str | None = None
    f8: str | None = None
    g8: str | None = None
    h8: str | None = None

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
                board_dict[key] = char
                index += 1
        return cls(**board_dict)

    def to_FEN(self) -> str:
        raise NotImplementedError
