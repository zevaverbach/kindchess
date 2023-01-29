import dataclasses as dc
import typing as t

Uid = t.NewType("Uid", str)
# not really a FEN, just the positions part
FEN = t.NewType("FEN", bytes)

Side = t.Literal[0, 1]
Castle = t.Literal["k", "q"]
Piece = t.Literal["q", "k", "b", "n", "r", "p"]
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
