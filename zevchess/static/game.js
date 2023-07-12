import {
    Chessboard,
    INPUT_EVENT_TYPE,
    MARKER_TYPE,
    COLOR,
} from './node_modules/cm-chessboard/src/cm-chessboard/Chessboard.js';

import {
    FEN
}
from './node_modules/cm-chessboard/src/cm-chessboard/model/Position.js';

import {
    store,
} from './store.js';

import {
    showStalemate,
    showCheckmate,
    showResignButton,
    showDrawButton,
    hideDrawOfferButton,
    changeModalText,
    hideDrawAcceptAndRejectButtons,
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
if (["127.0.0.1:5000", "localhost:8000"].includes(window.location.host)) {
    WEBSOCKET_SERVER_ADDR = 'ws://0.0.0.0:8081/';
} else {
    WEBSOCKET_SERVER_ADDR = 'wss://ws.kindchess.com';
}
// five minutes
const _TIMEOUT_DISCONNECTED_GAMES_MINUTES = 1;
const TIMEOUT_DISCONNECTED_GAMES_MS = 1000 * 60 * _TIMEOUT_DISCONNECTED_GAMES_MINUTES;
store.disconnectTimeoutCountdownSeconds = TIMEOUT_DISCONNECTED_GAMES_MS / 1000;
const MAX_REJOIN_ATTEMPTS = 3;

// hopefully prevents pinch to zoom
document.addEventListener('touchmove', e => {
    if (e.touches.length > 1) {
        e.preventDefault();
    }
}, {
    passive: false
})


let board, pawnPromotionSquare, pawnPromotionMove;
let myTurn = false;
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
store.numTimesSentRejoinMessage = 0;
store.side = null;
store.otherSide = null;
store.selfDrawOffer = false;
store.otherDrawOffer = false;
store.canOfferDraw = false;

store.uid = window.location.pathname.replace('/', '');
store.pendingTimeout = null;
store.disconnectIntervalID = null;

const choosePawnPromotionPiece = document.getElementById("pawn-promote");
choosePawnPromotionPiece.addEventListener('cancel', event => {
    event.preventDefault();
});

const choosePawnPromotionPieceSelect = choosePawnPromotionPiece.querySelector("select");
choosePawnPromotionPieceSelect.addEventListener("change", function(_) {
    pawnPromotionPiece = choosePawnPromotionPieceSelect.value;
    const pieceLetter = pawnPromotionPiece === "Knight" ? "n" : pawnPromotionPiece[0].toLowerCase();
    const piece = `${store.side[0]}${pieceLetter}`;
    board.setPiece(pawnPromotionSquare, piece);
});


function beforeUnloadListener(e) {
    e.preventDefault();
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

window.addEventListener('DOMContentLoaded', start);

function start() {
    store.ws = new WebSocket(WEBSOCKET_SERVER_ADDR);
    joinGame();
    receiveMessages();
    choosePawnPromotionPiece.addEventListener("close", pawnPromotionHandler)
};


function pawnPromotionHandler() {
    store.ws.send(JSON.stringify({
        type: "pawn_promote",
        'uid': store.uid,
        choice: pawnPromotionPiece === "Knight" ? "n" : pawnPromotionPiece.toLowerCase()[0],
        move: JSON.stringify(pawnPromotionMove),
    }));
    pawnPromotionSquare = null;
    pawnPromotionPiece = "Queen";
    pawnPromotionMove = null;
}

function itsBeenLessThan(timestamp, threshold) {
    const result = new Date().getTime() - timestamp;
    console.log("new Date().getTime():", result);
    if (result < threshold);
    return result;
}

function joinGame() {
    store.ws.addEventListener('open', handlerWebsocketOpen);
    store.ws.addEventListener('close', handlerWebsocketClose);
}

function handlerWebsocketOpen(_) {
    sendJoinOrRejoinMessage()
}

function sendJoinOrRejoinMessage() {
    store.numTimesSentRejoinMessage += 1;
    let messageObj = {
        type: 'join',
        'uid': store.uid,
    };
    if (localStorage.getItem('uid') && localStorage.getItem('uid') === store.uid) {
        const disconnectedTimestamp = parseInt(localStorage.getItem('disconnectedTimestamp'));
        if (localStorage.getItem('side') !== "undefined" && itsBeenLessThan(disconnectedTimestamp, TIMEOUT_DISCONNECTED_GAMES_MS)) {
            messageObj.type = 'rejoin';
            messageObj.side = localStorage.getItem('side');
            messageObj.disconnected_timestamp = disconnectedTimestamp;
        }
    }
    const message = JSON.stringify(messageObj);
    console.log("sending message type:", messageObj.type);
    store.ws.send(message);
};

function handlerWebsocketClose(_) {
    const disconnectedTimestamp = new Date().getTime().toString();
    localStorage.setItem("disconnectedTimestamp", disconnectedTimestamp);
    if (board != null) {
        board.disableMoveInput();
    }
    changeModalText("Connection lost. Attempting to reconnect...");

    removeEventListeners();

    store.disconnectIntervalID = setTimeout(function() {
        store.disconnectTimeoutCountdownSeconds -= 1;
        if (store.disconnectTimeoutCountdownSeconds <= 0) {
            changeModalText("Connection lost. Attempting to reconnect...");
            clearTimeout(store.disconnectIntervalID);
            store.disconnectIntervalID = null;
        };
        changeModalText(`Connection lost. Attempting to reconnect... (${store.disconnectTimeoutCountdownSeconds} seconds)`);
        start();
    }, 1000)
}

function removeEventListeners() {
    choosePawnPromotionPiece.removeEventListener("close", pawnPromotionHandler);
    store.ws.removeEventListener("message", messageHandler);
    store.ws.removeEventListener('open', handlerWebsocketOpen);
    store.ws.removeEventListener('close', handlerWebsocketClose);
}

function updateAbilityToOfferDraw() {
    const canOfferDrawAttrib = store.side === "white" ? "can_offer_draw_white" : "can_offer_draw_black";
    if (store.canOfferDraw != gameState[canOfferDrawAttrib]) {
        store.canOfferDraw = gameState[canOfferDrawAttrib];
        if (store.canOfferDraw && !store.selfDrawOffer && !store.otherDrawOffer) {
            showDrawButton();
        } else if (!store.canOfferDraw) {
            hideDrawOfferButton();
        }
    }
}

function updatePendingDrawReceive() {
    if (store.selfDrawOffer) {
        hideWithdrawDrawButton();
        store.selfDrawOffer = false;
    }
}

function updatePendingDrawSend() {
    if (store.otherDrawOffer) {
        store.otherDrawOffer = false;
        hideDrawAcceptAndRejectButtons();
        if (store.canOfferDraw) {
            showDrawButton();
        }
    }
}

function receiveMessages() {
    store.ws.addEventListener('message', messageHandler);
}

function messageHandler(message) {
    let ev;
    try {
        ev = JSON.parse(message.data);
    } catch (e) {
        console.log(message.data);
        throw e;
    }

    switch (ev.type) {

        case 'join_success':
            updateGlobals(ev);
            handleEventJoinSuccess(ev);
            storeGameInLocalStorage();
            break;

        case 'rejoin_success':
            hideModal();
            clearInterval(store.disconnectIntervalID);
            localStorage.removeItem('disconnectedTimestamp');
            store.side = localStorage.getItem('side');
            if (ev.hasOwnProperty('game_state')) {
                updateGlobals(ev);
            }
            drawBoardIfNecessary(gameState.FEN);
            if (myTurn) {
                sendMoves(); // this re-enables input on the board
            }
            break;

        case 'disconnect':
            console.log('received disconnect message', ev);
            localStorage.setItem('disconnectedTimestamp', ev.disconnected_timestamp);
            board.disableMoveInput();
            displayModal(`${store.otherSide} has disconnected. Waiting...`);
            console.log("disconnectTimeoutCountdownSeconds", store.disconnectTimeoutCountdownSeconds);
            clearMessage();
            store.disconnectIntervalID = setInterval(function() {
                store.disconnectTimeoutCountdownSeconds -= 1;
                console.log("disconnectTimeoutCountdownSeconds", store.disconnectTimeoutCountdownSeconds);
                if (store.disconnectTimeoutCountdownSeconds <= 0) {
                    changeModalText(`${store.otherSide} has disconnected. Waiting...`, false);
                    clearTimeout(store.disconnectIntervalID);
                };
                changeModalText(`${store.otherSide} has disconnected. Waiting (${store.disconnectTimeoutCountdownSeconds} seconds before terminating the game in ${store.side}'s favor)`);
            }, 1000);
            break;

        case 'for_the_watchers':
            displayMessage(ev.message);
            break;

        case 'success':
            if (ev.move.castle) {
                doTheMoveSentCastle(ev.move, board);
            } else if (isEnPassantMove(ev.move, board)) {
                doTheMoveSentEnPassant(ev.move, board);
            } else {
                updateGlobals(ev);
                updateAbilityToOfferDraw()
                updateCheckStatus(gameState, checkedKing, setCheckedKing);
            }
            break;

        case 'move':
            const move = ev.move;
            updateGlobals(ev);
            updateAbilityToOfferDraw();
            updatePendingDrawReceive();
            const [from, to] = doTheMoveReceived(move, board);
            highlightPrevMove(from, to, prevMoveOrigin, prevMoveDest, setPrevMove, board);
            updateCheckStatus(gameState, checkedKing, setCheckedKing);
            myTurn = true;
            sendMoves();
            break;

        case 'draw_offer':
            document.dispatchEvent(new CustomEvent('drawOffer', {
                detail: {
                    message: {
                        source: 'other',
                        message: ev.message,
                    },
                },
            }));
            break;

        case 'draw_withdraw':
            document.dispatchEvent(new CustomEvent('drawWithdraw', {
                detail: {
                    message: {
                        source: 'other',
                        message: ev.message,
                    },
                },
            }));
            break;

        case 'draw_reject':
            document.dispatchEvent(new CustomEvent('drawReject', {
                detail: {
                    message: {
                        source: 'other',
                        message: ev.message,
                    },
                },
            }));
            break;

        case 'input_required':
            if (ev.message !== "choose pawn promotion piece") break;
            pawnPromotionSquare = ev.dest;
            pawnPromotionMove = ev.move;
            const queenPiece = `${store.side[0]}q`;
            board.setPiece(pawnPromotionSquare, queenPiece);
            choosePawnPromotionPiece.showModal();
            break;

        case 'error':
            if (ev.message === "invalid UID") {
                console.log("numTimesSentRejoinMessage", store.numTimesSentRejoinMessage);
                clearLocalStorage();
                if (store.numTimesSentRejoinMessage > MAX_REJOIN_ATTEMPTS) {
                    return doGameOver(ev);
                }
                return sendJoinOrRejoinMessage();
            } else {
                console.log("error", ev);
            }
            break;
        case 'game_over':
            if (gameOver) { // already gameOver
                break;
            }
            doGameOver(ev);
            break;
    }
}

function doGameOver(ev) {
    console.log("game_over", ev);
    const winner = ev.winner;
    gameState = ev.game_state;
    hideButtons();
    clearMessage();
    if (winner != null && ev.reason === "checkmate") {
        showCheckmate(winner, gameState);
    } else if (ev.message === "stalemate!") {
        showStalemate(gameState);
    }
    displayModal("GAME OVER: " + ev.message);
    gameOver = true;
    clearLocalStorage();
    board.disableMoveInput();
    window.removeEventListener("beforeunload", beforeUnloadListener);
    console.log("closing websocket connection at ", new Date().getTime());
    store.ws.close();
    if (["game not found, redirecting to home page", "invalid UID"].includes(ev.message)) {
        setTimeout(function() {
            window.location.href = "/";
        }, 2000);
    }
}

function storeGameInLocalStorage() {
    localStorage.setItem('uid', store.uid);
    localStorage.setItem('side', store.side);
}

function clearLocalStorage() {
    localStorage.removeItem('uid');
    localStorage.removeItem('side');
    localStorage.removeItem('disconnectedTimestamp');
}

function unloadListener(e) {
    e.preventDefault();
    store.ws.close();
}


function handleEventJoinSuccess(event) {
    window.addEventListener("beforeunload", beforeUnloadListener);
    window.addEventListener("unload", unloadListener);
    if (event.game_status === 'waiting') {
        store.side = 'white';
        store.otherSide = 'black';
    } else {
        store.side = event.side;
        if (store.side) {
            store.otherSide = 'white'
            // otherwise it's a watcher
            clearMessage();
            showResignButton();
            hideModal();
            displayMessage('game on!');
        }
    }
    if (event.game_status === 'waiting' && store.side && store.side === 'white') {
        displayModal('waiting for black to join (share this URL with your friend!)');
    }
    if (store.side == 'white' && event.game_status === 'ready') {
        myTurn = true;
        sendMoves();
    } else {
        // game_status is 'waiting', so draw the board this one time.
        drawBoardIfNecessary();
    }
}

function drawBoardIfNecessary(position = FEN.start) {
    if (board == null) {
        board = new Chessboard(document.getElementById('board'), {
            position,
            orientation: store.side ? store.side[0] : "w", // if it's a watcher, display from white's POV
            style: {
                moveFromMarker: MARKER_TYPE.square,
                moveToMarker: MARKER_TYPE.square
            }, // disable standard markers
        });
    }
}

function sendMoves() {
    if (!myTurn) {
        return board.disableMoveInput();
    }
    console.log("enabling board input", new Date().getTime())
    board.enableMoveInput(
        function(event) {
            switch (event.type) {
                case INPUT_EVENT_TYPE.moveInputStarted:
                    return validateMoveInputStarted(event);
                case INPUT_EVENT_TYPE.moveInputCanceled:
                    board.removeDots();
                    break;
                case INPUT_EVENT_TYPE.validateMoveInput:
                    const result = sendMove(event);
                    updatePendingDrawSend();
                    return result
            }
        },
        store.side === 'black' ? COLOR.black : COLOR.white
    );
}

function sendMove(event) {
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
        if (capture) {
            move.capture = 1;
        }
        let promote = isPromotionMove(move);
        if (promote) {
            move.promote = 1;
        }
    }

    if (invalidMove(move, possibleMoves)) {
        board.removeDots();
        return false;
    }

    const msg = JSON.stringify({
        'uid': store.uid,
        type: 'move',
        ...move
    });
    store.ws.send(msg);
    highlightPrevMove(from, to, prevMoveOrigin, prevMoveDest, setPrevMove, board);

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
        } else if (mv.castle && getKingStartSquare(store.side) === event.square) {
            const rank = store.side === "black" ? 8 : 1;
            if (mv.castle === "k") {
                movesFromSquare.push({
                    dest: `g${rank}`
                })
            } else if (mv.castle === "q") {
                movesFromSquare.push({
                    dest: `c${rank}`
                });
            }
        }
    }
    for (const move of movesFromSquare) {
        board.addDot(move.dest);
    }
    return movesFromSquare.length > 0;
}
