import {
    store
} from './store.js';

export function getPieceAt(src, board) {
    const piece = board.getPiece(src);
    if (piece == null) return null;
    const [color, pieceName] = piece;
    return color === "b" ? pieceName : pieceName.toUpperCase();
}

export function getKingStartSquare() {
    return store.side === "black" ? "e8" : "e1"
}

function getLastRank() {
    return store.side === "black" ? 1 : 8;
}

export function isPromotionMove(move) {
    if (move.piece.toLowerCase() !== "p") return false;
    const [_, rank] = move.dest;
    return parseInt(rank) === getLastRank();
}

export function invalidMove(move, possibleMoves) {
    return !possibleMoves.some(pm =>
        // double equals because some of these attributes may be 'undefined' on one side
        // and null on the other
        pm.src == move.src &&
        pm.dest == move.dest &&
        pm.piece == move.piece &&
        pm.capture == move.capture &&
        pm.castle == move.castle
    )
}

export function isCaptureMove(event, piece, board) {
    const thereIsAPieceAtDest = getPieceAt(event.squareTo, board);
    if (thereIsAPieceAtDest) {
        return 1;
    }
    if (piece.toLowerCase() === "p") {
        const [fileSource, rankSourceStr] = event.squareFrom;
        const [fileDest, rankDestStr] = event.squareTo;
        const fileSourceIndex = "abcdefgh".indexOf(fileSource);
        const fileDestIndex = "abcdefgh".indexOf(fileDest);
        const rankSource = parseInt(rankSourceStr);
        const rankDest = parseInt(rankDestStr);
        if (
            Math.abs(fileSourceIndex - fileDestIndex) === 1 &&
            Math.abs(rankDest - rankSource) === 1
        ) {
            return 1;
        }
    }
    return 0;
}

export function isCastlingMove(event, piece) {
    return (
        piece.toLowerCase() === "k" &&
        (event.squareFrom[0] === "e" && ["g", "c"].includes(event.squareTo[0]))
    );
}

export function isEnPassantMove(move, board) {
    if (!move.dest) {
        return false;
    }
    const [file, rankStr] = move.dest;
    const rank = parseInt(rankStr);
    const spaceBehindDest = store.side === "black" ? `${file}${rank + 1}` : `${file}${rank - 1}`;
    return (
        move.piece.toLowerCase() == "p" &&
        move.capture === 1 &&
        getPieceAt(spaceBehindDest, board) == toggleCase(move.piece)
    );
}

function toggleCase(str) {
    if (str.toUpperCase() === str) {
        return str.toLowerCase();
    }
    return str.toUpperCase();
}
