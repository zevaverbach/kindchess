// TODO: break this up into multiple modules
import {
  Chessboard,
  INPUT_EVENT_TYPE,
  MARKER_TYPE,
  COLOR,
} from './node_modules/cm-chessboard/src/cm-chessboard/Chessboard.js';

import { FEN } 
  from './node_modules/cm-chessboard/src/cm-chessboard/model/Position.js';

import { showShareButton, showStalemate, showCheckmate, updateCheckStatus } from './domOps.js';
import { getPieceAt, getKingStartSquare, invalidMove, isCaptureMove, isCastlingMove, isEnPassantMove, isPromotionMove } from './boardOps.js';
import { doTheMoveReceived, doTheMoveSentEnPassant, doTheMoveSentCastle } from './moveOps.js';

let WEBSOCKET_SERVER_ADDR;
if (window.location.host === "localhost:8000") {
  WEBSOCKET_SERVER_ADDR = 'ws://0.0.0.0:8080/'
} else {
  WEBSOCKET_SERVER_ADDR = 'wss://zevchess-ws-zyr9.onrender.com'
}
let side, board, messageBox, pawnPromotionSquare, pawnPromotionMove;
let myTurn = false;
let testing = false;
let gameOver = false;
let gameState = {};
let boardArray = [];
let possibleMoves = [];

let checkedKing = "";
function setCheckedKing(val) {
  checkedKing = val;
}

let pawnPromotionPiece = "Queen";
const uid = window.location.pathname.replace('/', '');



const main = document.getElementsByTagName('main')[0];
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

window.addEventListener('DOMContentLoaded', function () {
  messageBox = document.getElementById('messagebox');
  const ws = new WebSocket(WEBSOCKET_SERVER_ADDR);
  joinGame(ws);
  receiveMessages(ws);
  if (side) {
    displayMessage('waiting for black to join', false);
  }
  choosePawnPromotionPiece.addEventListener("close", function() {
    ws.send(JSON.stringify({
      type: "pawn_promote",
      uid,
      choice: pawnPromotionPiece === "Knight" ? "n" : pawnPromotionPiece.toLowerCase()[0],
      move: JSON.stringify(pawnPromotionMove),
    }));
    pawnPromotionSquare = null;
    pawnPromotionPiece = "Queen";
    pawnPromotionMove = null;
  });
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
    if (testing) wsMessageElement.value = wsMessageElement.value + `\nreceived:\n ${message.data}\n`;

    switch (event.type) {

      case 'join_success':
        updateGlobals(event);
        handleEventJoinSuccess(event, ws);
        break;

      case 'success':
        // TODO: remove the next four lines 
        if (event.message !== "move acknowledged" || myTurn) {
          console.log("there was a message 'success' without the 'move acknowledged' message or !myTurn");
          break;
        }

        if (event.move.castle) {
          doTheMoveSentCastle(event.move, side, board);
        } else if (isEnPassantMove(event.move, board, side)) {
          doTheMoveSentEnPassant(event.move, board, side);
        } else {
          const gameState = event.game_state;
          // TODO: remove the next five lines 
          console.log(gameState);
          if (gameState == undefined) {
            console.log('gameState is undefined for some reason');
            break;
          }
          updateCheckStatus(gameState, checkedKing, setCheckedKing);
        }
        break;

      case 'move':
        const move = event.move;
        doTheMoveReceived(move, board, side);
        updateGlobals(event);
        updateCheckStatus(gameState, checkedKing, setCheckedKing);
        myTurn = true;
        sendMoves(ws);
        break;

      case 'input_required':
        if (event.message !== "choose pawn promotion piece") break;
        pawnPromotionSquare = event.dest;
        pawnPromotionMove = event.move;
        const queenPiece = `${side[0]}q`;
        board.setPiece(pawnPromotionSquare, queenPiece);
        choosePawnPromotionPiece.showModal();
        break;

      case 'game_over':
        if (gameOver) { // already gameOver
          break;
        }
        const winner = event.winner;
        gameState = event.game_state;
        // TODO: remove
        console.log(gameState);
        if (winner != null) {
          showCheckmate(winner, gameState);
        } else if (event.message === "stalemate!") {
          showStalemate(gameState);
        }
        displayMessage(event.message, false);
        gameOver = true;
        window.removeEventListener("beforeunload", beforeUnloadListener);
        ws.close();
        break;
    }
  });
}

function handleEventJoinSuccess(event, ws) {
  if (event.game_status === 'waiting') {
    side = 'white';
  } else {
    side = event.side;
    // otherwise it's a watcher
    if (side) {
      clearMessage();
      displayMessage('game on!');
    }
  }
  showShareButton(main);
  if (side == 'white' && event.game_status === 'ready') {
    myTurn = true;
    sendMoves(ws);
  } else {
    // game_status is 'waiting', so draw the board this one time.
    board = new Chessboard(document.getElementById('board'), {
      position: FEN.start,
      orientation: side ? side[0] : "w", // if it's a watcher, display from white's POV
      style: {moveFromMarker: undefined, moveToMarker: undefined}, // disable standard markers
    });
  }
}

function sendMoves(ws) {
  if (!myTurn) {
    return board.disableMoveInput();
  }
  board.enableMoveInput(
    function (event) {
      switch (event.type) {
        case INPUT_EVENT_TYPE.moveInputStarted:
          return validateMoveInputStarted(event);
        case INPUT_EVENT_TYPE.moveInputCanceled:
          event.chessboard.removeMarkers(MARKER_TYPE.dot);
          break;
        case INPUT_EVENT_TYPE.validateMoveInput:
          return sendMove(event, ws);
      }
    },
    side === 'black' ? COLOR.black : COLOR.white
  );
}

function sendMove(event, ws) {
  const piece = getPieceAt(event.squareFrom, board);
  let move = {
    piece: null,
    src: null,
    dest: null,
  };

  if (isCastlingMove(event, piece)) {
    move.castle = event.squareTo[0] === "c" ? "q" : "k";
  } else {
    move.piece = piece;
    move.src = event.squareFrom;
    move.dest = event.squareTo;
    let capture = isCaptureMove(event, piece, board);
    if (capture) move.capture = 1;
    let promote = isPromotionMove(move, side);
    if (promote) move.promote = 1;
  }

  if (invalidMove(move, possibleMoves)) {
    console.log('invalid move');
    console.log(move);
    console.log(possibleMoves);
    return false
  }

  const msg = JSON.stringify({uid, type: 'move', ...move});
  ws.send(msg);

  if (testing) wsMessageElement.value = wsMessageElement.value + `\nsent:\n ${msg}\n`;

  myTurn = false;
  event.chessboard.removeMarkers(MARKER_TYPE.dot);
  board.disableMoveInput();
  return true;
}


function displayMessage(message, timeout = true) {
  messageBox.innerHTML = message;
  if (timeout) {
    setTimeout(function () {
      messageBox.innerHTML = '';
    }, 3000);
  }
}

function clearMessage() { messageBox.innerHTML = ""; }

const choosePawnPromotionPiece = document.getElementById("pawn-promote");
const choosePawnPromotionPieceSelect = choosePawnPromotionPiece.querySelector("select");
choosePawnPromotionPieceSelect.addEventListener("change", function(e) {
  pawnPromotionPiece = choosePawnPromotionPieceSelect.value;
  const pieceLetter = pawnPromotionPiece === "Knight" ? "n" : pawnPromotionPiece[0].toLowerCase();
  const piece = `${side[0]}${pieceLetter}`;
  board.setPiece(pawnPromotionSquare, piece);
});

function updateGlobals(event) {
  gameState = event.game_state;
  console.log(gameState);
  boardArray = event.board;
  possibleMoves = event.possible_moves;
}

function validateMoveInputStarted(event) {
  event.chessboard.removeMarkers(MARKER_TYPE.dot);
  let movesFromSquare = [];
  for (const mv of possibleMoves) {
    if (mv.src === event.square) {
      movesFromSquare.push(mv);
    } else if (mv.castle && getKingStartSquare() === event.square) {
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
}
