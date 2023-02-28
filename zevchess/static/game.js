import {
  Chessboard,
  INPUT_EVENT_TYPE,
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
console.log("WEBSOCKET_SERVER_ADDR:", WEBSOCKET_SERVER_ADDR);
let side, board, messageBox;
let myTurn = false;
let gameState = {};
let gameOver = false;
let boardArray = [];
let possibleMoves = [];
let checkedKing = "";
const main = document.getElementsByTagName('main')[0];

let testing = false;

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
          if (!side) {
            // it's a watcher
          } else {
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
          });
        }
        if (myTurn) sendMoves(ws);
        break;
      case 'success':
        if (event.message !== "move acknowledged" || myTurn) break;
        if (event.move.castle) {
          const rank = side === "black" ? 8 : 1; // it's this side that castled
          if (event.move.castle === "k") {
            board.movePiece(`h${rank}`, `f${rank}`, true)
          } else {
            board.movePiece(`a${rank}`, `d${rank}`, true)
          }
        } else {
          const gameState = event.game_state;
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
          board
            .movePiece(move.src, move.dest, true).then(_ => null);
        }
        gameState = event.game_state;
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
        break;
    }
  });
}

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
            const moveSources = possibleMoves.map(mv => mv.castle ? getKingStartSquare(side) : mv.src)
            return moveSources.includes(event.square);
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
              const capture = getPieceAt(event.squareTo) ? 1 : 0;
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
              console.log('denied move:', move)
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
