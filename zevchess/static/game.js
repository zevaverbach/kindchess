import {
  Chessboard,
  INPUT_EVENT_TYPE,
  MARKER_TYPE,
  COLOR,
} from './node_modules/cm-chessboard/src/cm-chessboard/Chessboard.js';

import { FEN } 
  from './node_modules/cm-chessboard/src/cm-chessboard/model/Position.js';

let WEBSOCKET_SERVER_ADDR;
if (window.location.host === "localhost:8000") {
  WEBSOCKET_SERVER_ADDR = 'ws://0.0.0.0:8001/'
} else {
  WEBSOCKET_SERVER_ADDR = 'wss://zevchess-ws-zyr9.onrender.com'
}
let side, board, messageBox;
let myTurn = false;
let gameState = {};
let gameOver = false;
let boardArray = [];
let possibleMoves = [];
let checkedKing = "";
const main = document.getElementsByTagName('main')[0];

let testing = false;

window.addEventListener("beforeunload", beforeUnloadListener);

function beforeUnloadListener(e) {
  e.preventDefault();
  return "are you sure you want to abandon this game?";
}

if (testing) {
  const div = document.createElement('div');
  div.innerHTML = "<textarea readonly id='ws'></textarea>";
  const wsMessageElement = div.firstChild;
}
const uid = window.location.pathname.replace('/', '');

function displayMessage(message, timeout = true) {
  messageBox.innerHTML = message;
  if (timeout) {
    setTimeout(function () {
      messageBox.innerHTML = '';
    }, 3000);
  }
}

function clearMessage() { messageBox.innerHTML = ""; }

window.addEventListener('DOMContentLoaded', function () {
  messageBox = document.getElementById('messagebox');
  const ws = new WebSocket(WEBSOCKET_SERVER_ADDR);
  joinGame(ws);
  receiveMessages(ws);
  if (side) {
    displayMessage('waiting for black to join', false);
  }
});

function joinGame(ws) {
  ws.addEventListener('open', function (event) {
    const message = JSON.stringify({
      type: 'join',
      uid,
    });
    ws.send(message);
    if (testing)
      wsMessageElement.value =
        wsMessageElement.value + `\nsent:\n ${message}\n`;
  });
  ws.addEventListener('close', function (event) {
  })
}

function receiveMessages(ws) {
  ws.addEventListener('message', function (message) {
    const event = JSON.parse(message.data);
    if (testing)
      wsMessageElement.value =
        wsMessageElement.value + `\nreceived:\n ${message.data}\n`;
    switch (event.type) {
      case 'join_success':
        gameState = event.game_state;
        boardArray = event.board;
        possibleMoves = event.possible_moves;
        if (event.game_status === 'waiting') {
          side = 'white';
        } else {
          side = event.side;
          if (side) {
            clearMessage();
            displayMessage('game on!');
          }
        }
        showShareButton();
        if (side == 'white' && event.game_status === 'ready') {
          myTurn = true;
        } else {
          // game_status is 'waiting', so draw the board this one time.
          board = new Chessboard(document.getElementById('board'), {
            position: FEN.start,
            orientation: side ? side[0] : "w", // if it's a watcher, display from white's POV
            style: {moveFromMarker: undefined, moveToMarker: undefined}, // disable standard markers
          });
          // window.board = board;
        }
        if (myTurn) sendMoves(ws);
        break;
      case 'success':
        if (event.message !== "move acknowledged" || myTurn) break;
        let enPassant = false;
        if (event.move.dest) {
          const [file, rankStr] = event.move.dest;
          const rank = parseInt(rankStr);
          const spaceBehindDest = side === "black" ? `${file}${rank + 1}` : `${file}${rank - 1}`;
          enPassant = (
            event.move.piece.toLowerCase() == "p" 
            && event.move.capture === 1 
            && getPieceAt(spaceBehindDest) == toggleCase(event.move.piece)
          );
        }
        if (event.move.castle) {
          const rank = side === "black" ? 8 : 1; // it's this side that castled
          if (event.move.castle === "k") {
            board.movePiece(`h${rank}`, `f${rank}`, true)
          } else {
            board.movePiece(`a${rank}`, `d${rank}`, true)
          }
        } else if (enPassant) {
          const [file, rankStr] = event.move.dest;
          const rank = parseInt(rankStr);
          const sq = side === "black" ? `${file}${rank + 1}` : `${file}${rank - 1}`;
          board.setPiece(sq, null);
        } else {
          const gameState = event.game_state;
          console.log(gameState);
          if (gameState == undefined) break;
          if ([0, 1].includes(gameState.its_check)) {
            checkedKing = gameState.its_check === 0 ? gameState.king_square_white: gameState.king_square_black;
            document.querySelector(`[data-square="${checkedKing}"]`).classList.add("check")
          } else if (checkedKing) {
              const query = `[data-square="${checkedKing}"]`
              document.querySelector(query).classList.remove("check")
              checkedKing = "";
          }
        }
        break;
      case 'move':
        const move = event.move;
        if (move.castle) {
          const rank = side === "black" ? 1 : 8; // it's the other side that castled
          if (move.castle === "k") {
            board.movePiece(`e${rank}`, `g${rank}`, true)
            board.movePiece(`h${rank}`, `f${rank}`, true)
          } else {
            board.movePiece(`e${rank}`, `c${rank}`, true)
            board.movePiece(`a${rank}`, `d${rank}`, true)
          }
        } else {
          const enPassant = move.capture === 1 && getPieceAt(move.dest) == null
          board
            .movePiece(move.src, move.dest, true).then(_ => {
              if (enPassant) {
                const [file, rankStr] = move.dest;
                const rank = parseInt(rankStr);
                const sq = side === "black" ? `${file}${rank - 1}` : `${file}${rank + 1}`;
                board.setPiece(sq, null);
            };
          });
        }
        gameState = event.game_state;
        console.log(gameState);
        boardArray = event.board;
        possibleMoves = event.possible_moves;
        if (gameState) {
          if ([0, 1].includes(gameState.its_check)) {
            checkedKing = gameState.its_check === 0 ? gameState.king_square_white: gameState.king_square_black;
            document.querySelector(`[data-square="${checkedKing}"]`).classList.add("check")
          } else if (checkedKing) {
              const query = `[data-square="${checkedKing}"]`
              document.querySelector(query).classList.remove("check")
              checkedKing = "";
          }
        }
        myTurn = true;
        sendMoves(ws);
        break;
      case 'game_over':
        if (gameOver) break;
        const winner = event.winner;
        gameState = event.game_state;
        console.log(gameState);
        if (winner != null) {
          const checkmatedKingSquare = winner === "black" ? gameState.king_square_white: gameState.king_square_black;
          const selector = `[data-square="${checkmatedKingSquare}"]`;
          document.querySelector(selector).classList.add("mate");
        } else if (event.message === "stalemate!") {
          for (const color of ["white", "black"]) {
            const selector = `[data-square="${gameState['king_square_' + color]}"]`;
            document.querySelector(selector).classList.add("stale");
          }
        }
        displayMessage(event.message, false);
        gameOver = true;

        window.removeEventListener("beforeunload", beforeUnloadListener);
        break;
    }
  });
}

window.addEventListener("beforeunload", function(e) {
  e.preventDefault();
  return "are you sure you want to abandon this game?";
})


function showShareButton() {
  if (document.getElementById('share-button')) return
  const url = window.location.href;
  const shareButton = document.createElement("button");
  shareButton.id = "share-button";
  shareButton.addEventListener('click', () => {
    navigator.clipboard.writeText(url);
    displayMessage(
      `I've copied the following to your clipboard: ${url}, 
       feel free to share it with whoever you want to play against. 
       I'll let you know when they've joined!`, false
      )    
  })
  shareButton.innerText = "share invite URL"
  main.appendChild(shareButton);
}

function sendMoves(ws) {
  if (!myTurn) {
    board.disableMoveInput();
  } else {
    board.enableMoveInput(
      function (event) {
        switch (event.type) {
          case INPUT_EVENT_TYPE.moveInputStarted:
            event.chessboard.removeMarkers(MARKER_TYPE.dot);
            let movesFromSquare = [];
            for (const mv of possibleMoves) {
              if (mv.src === event.square) {
                movesFromSquare.push(mv);
              } else if (mv.castle && getKingStartSquare(side) === event.square) {
                const rank = side === "black" ? 8 : 1;
                if (mv.castle === "k") {
                  movesFromSquare.push({dest: `g${rank}`})
                } else if (mv.castle === "q") {
                  movesFromSquare.push({dest: `c${rank}`})
                }
              }
            }
            for (const move of movesFromSquare) {
              event.chessboard.addMarker(MARKER_TYPE.dot, move.dest);
            }
            return movesFromSquare.length > 0;
          case INPUT_EVENT_TYPE.moveInputCanceled:
            event.chessboard.removeMarkers(MARKER_TYPE.dot);
          case INPUT_EVENT_TYPE.validateMoveInput:
            const piece = getPieceAt(event.squareFrom);
            let move = {
              piece: null,
              src: null,
              dest: null,
            };
            if (piece.toLowerCase() === "k" && (event.squareFrom[0] === "e" && ["g", "c"].includes(event.squareTo[0]))) {
              move.castle = event.squareTo[0] === "c" ? "q" : "k";
            } else {
              move.piece = piece;
              move.src = event.squareFrom;
              move.dest = event.squareTo;
              const thereIsAPieceAtDest = getPieceAt(event.squareTo);
              let capture = thereIsAPieceAtDest ? 1 : 0;
              // check if it's en passant
              if (!capture && piece.toLowerCase() === "p") {
                const [fileSource, rankSourceStr] = event.squareFrom;
                const [fileDest, rankDestStr] = event.squareTo;
                const fileSourceIndex = "abcdefgh".indexOf(fileSource);
                const fileDestIndex = "abcdefgh".indexOf(fileDest);
                const rankSource = parseInt(rankSourceStr);
                const rankDest = parseInt(rankDestStr);
                if (Math.abs(fileSourceIndex - fileDestIndex) === 1 
                    && Math.abs(rankDest - rankSource) === 1) 
                {
                  capture = 1;
                }
              }
              if (capture) {
                move.capture = capture;
              }
            }
            if (
              !possibleMoves.some(pm => 
                //  because some of these attributes may be undefined on one side
                // and null on the other
                pm.src == move.src && pm.dest == move.dest && pm.piece == move.piece 
                && pm.capture == move.capture && pm.castle == move.castle
              )
            ) {
              return false;
            }
            const msg = JSON.stringify({
              uid,
              type: 'move',
              ...move,
            });
            ws.send(msg);
            if (testing)
              wsMessageElement.value =
                wsMessageElement.value + `\nsent:\n ${msg}\n`;
            myTurn = false;
            event.chessboard.removeMarkers(MARKER_TYPE.dot);
            board.disableMoveInput();
            return true;
        }
      },
      side === 'black' ? COLOR.black : COLOR.white,
    );
  }
}

function getKingStartSquare(side) {
  return side === "black" ? "e8" : "e1"
}

function getPieceAt(src) {
  const piece = board.getPiece(src);
  if (piece == null) return null;
  const [color, pieceName] = piece;
  return color === "b" ? pieceName : pieceName.toUpperCase();
}

function doMoves(ws) {
  // TODO
}

function movePiece(src, dest, ws) {
  const piece = getPieceAt(src);
  let move = {
    piece: null,
    src: null,
    dest: null,
  };
  if (piece.toLowerCase() === "k" && (src[0] === "e" && ["g", "c"].includes(dest[0]))) {
    move.castle = dest[0] === "c" ? "q" : "k";
  } else {
    move.piece = piece;
    move.src = src;
    move.dest = dest;
    const capture = getPieceAt(move.dest) ? 1 : 0;
    if (capture) {
      move.capture = capture;
    }
  }
  const msg = JSON.stringify({
    uid,
    type: 'move',
    ...move,
  });
  ws.send(msg);
}

function toggleCase(str) {
  if (str.toUpperCase() === str) {
    return str.toLowerCase();
  }
  return str.toUpperCase();
}
