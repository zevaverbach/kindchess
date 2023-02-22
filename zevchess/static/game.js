import {
  Chessboard,
  INPUT_EVENT_TYPE,
  COLOR,

} from './node_modules/cm-chessboard/src/cm-chessboard/Chessboard.js';
import { FEN } 
  from './node_modules/cm-chessboard/src/cm-chessboard/model/Position.js';

let side, board, messageBox;
let myTurn = false;
let gameState = {};
let boardArray = [];
let turn = 1;
let possibleMoves = [];
let testing = false;
const main = document.getElementsByTagName('main')[0];

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
  displayMessage('waiting for black to join', false);
  const ws = new WebSocket('ws://0.0.0.0:8001/');
  joinGame(ws);
  receiveMessages(ws);
});

function joinGame(ws) {
  ws.addEventListener('open', function () {
    const message = JSON.stringify({
      type: 'join',
      uid,
    });
    ws.send(message);
    if (testing)
      wsMessageElement.value =
        wsMessageElement.value + `\nsent:\n ${message}\n`;
  });
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
          clearMessage();
          displayMessage('game on!');
        }
        showShareButton();
        if (side == 'white' && event.game_status === 'ready') {
          myTurn = true;
        } else {
          // game_status is 'waiting', so draw the board this one time.
          board = new Chessboard(document.getElementById('board'), {
            position: FEN.start,
            orientation: side[0],
          });
        }
        if (myTurn) sendMoves(ws);
        break;
      case 'move':
        const move = event.move;
        board
          .movePiece(move.src, move.dest, true) // `true` is for 'animated'
          .then((something) => console.log(something));
        gameState = event.game_state;
        boardArray = event.board;
        possibleMoves = event.possible_moves;
        console.log('possibleMoves:', possibleMoves);
        myTurn = true;
        sendMoves(ws);
      case 'game_over':
        displayMessage(event.message);
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
            const moveSources = possibleMoves.map((mv) => mv.src);
            return moveSources.includes(event.square);
          case INPUT_EVENT_TYPE.validateMoveInput:
            const move = {
              piece: getPieceAt(event.squareFrom),
              src: event.squareFrom,
              dest: event.squareTo,
            };
            const capture = getPieceAt(event.squareTo) ? 1 : 0;
            if (capture) {
              move.capture = capture;
            }
            if (
              !possibleMoves.some(
                (pm) =>
                  pm.src === move.src &&
                  pm.dest === move.dest &&
                  pm.piece === move.piece &&
                  pm.capture === move.capture,
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
            board.disableMoveInput();
            return true;
        }
      },
      side === 'black' ? COLOR.black : COLOR.white,
    );
  }
}

function getPieceAt(src) {
  const piece = board.getPiece(src);
  if (piece == null) return null;
  const [color, pieceName] = piece;
  return color === "b" ? pieceName : pieceName.toUpperCase();
}
