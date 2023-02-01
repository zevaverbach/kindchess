"""
There's code here to do this without the subprocess call, but I couldn't get it to work:

https://sw.kovidgoyal.net/kitty/graphics-protocol/#a-minimal-example
"""
import pathlib as pl
import subprocess as sp

import chess
import chess.svg


def print_board_from_FEN(fen: str):
    board = chess.Board(fen)
    boardsvg = chess.svg.board(board=board)
    path = pl.Path("BoardVisualisedFromFEN.SVG")
    path.write_text(boardsvg)
    sp.call(f"kitty +kitten icat {path.name}", shell=True)
    path.unlink()
