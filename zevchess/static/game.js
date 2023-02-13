import { Chessboard, INPUT_EVENT_TYPE, BORDER_TYPE, MARKER_TYPE, COLOR } from "./node_modules/cm-chessboard/src/cm-chessboard/Chessboard.js"
import { FEN } from "./node_modules/cm-chessboard/src/cm-chessboard/model/Position.js"

const board = new Chessboard(
    document.getElementById("board"),
    {position: FEN.start},
);

let turn = 1;

function toggleTurn() {
    turn = + !turn;
    board.enableMoveInput(function (event) {
        console.log(event);
        switch (event.type) {
        case INPUT_EVENT_TYPE.moveInputStarted:
          console.log(`moveInputStarted: ${event.square}`)
          // return `true`, if input is accepted/valid, `false` aborts the interaction, the piece will not move
          return true
        case INPUT_EVENT_TYPE.validateMoveInput:
          console.log(`validateMoveInput: ${event.squareFrom}-${event.squareTo}`)
          // return true, if input is accepted/valid, `false` takes the move back
          return true
        case INPUT_EVENT_TYPE.moveInputCanceled:
          console.log(`moveInputCanceled`)
      }
   }, turn ? COLOR.black : COLOR.white)
};

toggleTurn();

const numberOfWatchers = 0;
const players = {
    black: null,
    white: null,
}
const gameState = {}
const uid = window.location.pathname.replace('/', '');

const wsMessageElement = document.getElementById('ws');

window.addEventListener("DOMContentLoaded", () => {
    const ws = new WebSocket("ws://localhost:8001/");
    joinGame(ws);
    receiveMoves(ws);
    sendMoves(ws);
})

function joinGame(ws) {
    ws.addEventListener("open", function() {
        const message = JSON.stringify({type: "join", uid})
        ws.send(message);
        wsMessageElement.value = wsMessageElement.value + `\nsent: ${message}\n`
    })
}

function receiveMoves(ws) {
    ws.addEventListener("message", function(message) {
        console.log(message.data)
        const event = JSON.parse(message.data)
        wsMessageElement.value = wsMessageElement.value + `\nreceived: ${message.data}\n`
        // TODO: in a case statement,
        //   if it's a move from a player other than this one, use `ground.move("a4", "a5")`
    }) 
}

function sendMoves(ws) {
    return null;
}
