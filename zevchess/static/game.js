import {
  Chessboard,
  INPUT_EVENT_TYPE,
  MARKER_TYPE,
  COLOR,
} from './node_modules/cm-chessboard/src/cm-chessboard/Chessboard.js';

import { FEN }
  from './node_modules/cm-chessboard/src/cm-chessboard/model/Position.js';

import {
  showShareButton,
  showStalemate,
  showCheckmate,
  showResignButton,
  showDrawButton,
  showDrawAcceptAndRejectButtons,
  hideShareButton,
  hideDrawAcceptAndRejectButtons,
  hideDrawButton,
  hideWithdrawDrawButton,
  hideButtons,
  clearMessage,
  updateCheckStatus,
  displayMessage,
  displayModal,
  hideModal,
  highlightPrevMove,
} from './domOps.js';

import {
  getPieceAt,
  getKingStartSquare,
  invalidMove,
  isCaptureMove,
  isCastlingMove,
  isEnPassantMove,
  isPromotionMove
} from './boardOps.js';

import {
  doTheMoveReceived,
  doTheMoveSentEnPassant,
  doTheMoveSentCastle
} from './moveOps.js';

// TODO: get this from environment
let WEBSOCKET_SERVER_ADDR;
if (window.location.host === "localhost:8000") {
  WEBSOCKET_SERVER_ADDR = 'ws://0.0.0.0:8080/'
} else {
  WEBSOCKET_SERVER_ADDR = 'wss://ws.kindchess.com'
}

let side, board, pawnPromotionSquare, pawnPromotionMove;
let myTurn = false;
let testing = false;
let gameOver = false;
let gameState = {};
let boardArray = [];
let possibleMoves = [];
let pawnPromotionPiece = "Queen";
let prevMoveOrigin;
let prevMoveDest;
function setPrevMove(orig, dest) {
  prevMoveOrigin = orig;
  prevMoveDest = dest;
}

let checkedKing = "";
function setCheckedKing(val) {
  checkedKing = val;
}

let selfDrawOffer = false;
function setSelfDrawOffer(val) {
  selfDrawOffer = val;
}
let otherDrawOffer = false;

const uid = window.location.pathname.replace('/', '');

const choosePawnPromotionPiece = document.getElementById("pawn-promote");
choosePawnPromotionPiece.addEventListener('cancel', event => {
  event.preventDefault();
});
const choosePawnPromotionPieceSelect = choosePawnPromotionPiece.querySelector("select");
choosePawnPromotionPieceSelect.addEventListener("change", function(e) {
  pawnPromotionPiece = choosePawnPromotionPieceSelect.value;
  const pieceLetter = pawnPromotionPiece === "Knight" ? "n" : pawnPromotionPiece[0].toLowerCase();
  const piece = `${side[0]}${pieceLetter}`;
  board.setPiece(pawnPromotionSquare, piece);
});

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

document.onreadystatechange = function() {
  if (document.readyState !== "complete") {
    document.querySelector("main").style.visibility = "hidden";
    document.querySelector("#loader").style.visibility = "visible";
  } else {
    document.querySelector("#loader").style.display = "none";
    document.querySelector("main").style.visibility = "visible";
  }
};

window.addEventListener('DOMContentLoaded', function() {
  const ws = new WebSocket(WEBSOCKET_SERVER_ADDR);
  joinGame(ws);
  receiveMessages(ws);
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
  ws.addEventListener('open', function(event) {
    const message = JSON.stringify({
      type: 'join',
      uid,
    });
    ws.send(message);
    if (testing)
      wsMessageElement.value =
        wsMessageElement.value + `\nsent:\n ${message}\n`;
  });
  ws.addEventListener('close', function(event) {
  })
}

function receiveMessages(ws) {
  ws.addEventListener('message', function(message) {
    let ev;
    try {
      ev = JSON.parse(message.data);
    } catch (e) {
      console.log(message.data);
      throw e;
    }
    if (testing) wsMessageElement.value = wsMessageElement.value + `\nreceived:\n ${message.data}\n`;

    switch (ev.type) {

      case 'join_success':
        updateGlobals(ev);
        handleEventJoinSuccess(ev, ws);
        break;

      case 'for_the_watchers':

        displayMessage(ev.message);
        break;

      case 'success':
        // TODO: remove the next four lines 
        if (ev.message !== "move acknowledged" || myTurn) {
          console.log("there was a message 'success' without the 'move acknowledged' message or !myTurn");
          break;
        }

        if (ev.move.castle) {
          doTheMoveSentCastle(ev.move, side, board);
        } else if (isEnPassantMove(ev.move, board, side)) {
          doTheMoveSentEnPassant(ev.move, board, side);
        } else {
          const gameState = ev.game_state;
          updateCheckStatus(gameState, checkedKing, setCheckedKing);
        }
        break;

      case 'move':
        const move = ev.move;
        if (selfDrawOffer) {
          selfDrawOffer = false;
          hideWithdrawDrawButton();
          showDrawButton();
          clearMessage();
        }
        const [from, to] = doTheMoveReceived(move, board, side);
        highlightPrevMove(from, to, prevMoveOrigin, prevMoveDest, setPrevMove, board);
        updateGlobals(ev);
        if (gameState.half_moves == 2) {
          showDrawButton(uid, ws, setSelfDrawOffer);
        }
        updateCheckStatus(gameState, checkedKing, setCheckedKing);
        myTurn = true;
        sendMoves(ws);
        break;

      case 'draw_offer':
        hideDrawButton();
        showDrawAcceptAndRejectButtons(ws, uid);
        displayMessage(ev.message, false);
        otherDrawOffer = true;
        break;

      case 'draw_withdraw':
        showDrawButton();
        hideDrawAcceptAndRejectButtons();
        clearMessage();
        displayMessage(ev.message);
        otherDrawOffer = false;
        break;

      case 'draw_reject':
        showDrawButton();
        hideWithdrawDrawButton();
        showDrawButton();
        selfDrawOffer = false;
        displayMessage(ev.message);
        break;

      case 'input_required':
        if (ev.message !== "choose pawn promotion piece") break;
        pawnPromotionSquare = ev.dest;
        pawnPromotionMove = ev.move;
        const queenPiece = `${side[0]}q`;
        board.setPiece(pawnPromotionSquare, queenPiece);
        choosePawnPromotionPiece.showModal();
        break;

      case 'game_over':
        if (gameOver) { // already gameOver
          break;
        }
        const winner = ev.winner;
        gameState = ev.game_state;
        hideButtons();
        if (winner != null && ev.reason === "checkmate") {
          showCheckmate(winner, gameState);
        } else if (ev.message === "stalemate!") {
          showStalemate(gameState);
        }
        displayModal("GAME OVER: " + ev.message);
        hideShareButton();
        gameOver = true;
        board.disableMoveInput();
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
    if (side) {
      // otherwise it's a watcher
      clearMessage();
      showResignButton(uid, ws);
      if (side === "white") {
        hideModal();
      }
      displayMessage('game on!');
    }
  }
  showShareButton();
  if (event.game_status === 'waiting' && side && side === 'white') {
    console.log('displaying modal hopefully');
    displayModal('waiting for black to join');
  } else {
    console.log("didn't display modal because side is", side);
  }
  if (side == 'white' && event.game_status === 'ready') {
    myTurn = true;
    sendMoves(ws);
  } else {
    // game_status is 'waiting', so draw the board this one time.
    board = new Chessboard(document.getElementById('board'), {
      position: FEN.start,
      orientation: side ? side[0] : "w", // if it's a watcher, display from white's POV
      style: { moveFromMarker: MARKER_TYPE.square, moveToMarker: MARKER_TYPE.square }, // disable standard markers
    });
    window.B = board;
  }
}

function sendMoves(ws) {
  if (!myTurn) {
    return board.disableMoveInput();
  }
  board.enableMoveInput(
    function(event) {
      switch (event.type) {
        case INPUT_EVENT_TYPE.moveInputStarted:
          return validateMoveInputStarted(event);
        case INPUT_EVENT_TYPE.moveInputCanceled:
          board.removeDots();
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

  let to, from;
  if (isCastlingMove(event, piece)) {
    move.castle = event.squareTo[0] === "c" ? "q" : "k";
    [to, from] = [event.squareTo, event.squareFrom];
  } else {
    move.piece = piece;
    from = move.src = event.squareFrom;
    to = move.dest = event.squareTo;
    let capture = isCaptureMove(event, piece, board);
    if (capture) move.capture = 1;
    let promote = isPromotionMove(move, side);
    if (promote) move.promote = 1;
  }

  if (invalidMove(move, possibleMoves)) {
    return false
  }

  if (otherDrawOffer) {
    otherDrawOffer = false;
    hideDrawAcceptAndRejectButtons();
    showDrawButton();
    clearMessage();
  }
  if (gameState.half_moves == 1) {
    showDrawButton(uid, ws, setSelfDrawOffer);
  }
  const msg = JSON.stringify({ uid, type: 'move', ...move });
  ws.send(msg);
  highlightPrevMove(from, to, prevMoveOrigin, prevMoveDest, setPrevMove, board);
  if (testing) wsMessageElement.value = wsMessageElement.value + `\nsent:\n ${msg}\n`;

  myTurn = false;
  board.removeDots();
  board.disableMoveInput();
  return true;
}

function updateGlobals(event) {
  gameState = event.game_state;
  boardArray = event.board;
  possibleMoves = event.possible_moves;
}

function validateMoveInputStarted(event) {
  board.removeDots();
  let movesFromSquare = [];
  for (const mv of possibleMoves) {
    if (mv.src === event.square) {
      movesFromSquare.push(mv);
    } else if (mv.castle && getKingStartSquare(side) === event.square) {
      const rank = side === "black" ? 8 : 1;
      if (mv.castle === "k") {
        movesFromSquare.push({ dest: `g${rank}` })
      } else if (mv.castle === "q") {
        movesFromSquare.push({ dest: `c${rank}` });
      }
    }
  }
  for (const move of movesFromSquare) {
    board.addDot(move.dest);
  }
  return movesFromSquare.length > 0;
}
