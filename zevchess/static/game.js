import { Chessboard, INPUT_EVENT_TYPE, BORDER_TYPE, MARKER_TYPE, COLOR } from "./node_modules/cm-chessboard/src/cm-chessboard/Chessboard.js"
import { FEN } from "./node_modules/cm-chessboard/src/cm-chessboard/model/Position.js"

const numberOfWatchers = 0;

let side;
let myTurn = false;
let gameState = {}
let boardArray = []
const uid = window.location.pathname.replace('/', '');
let turn = 1;
let board;

const wsMessageElement = document.getElementById('ws');

window.addEventListener("DOMContentLoaded", function() {
    const ws = new WebSocket("ws://0.0.0.0:8001/");
    joinGame(ws);
    receiveMoves(ws);
})


function joinGame(ws) {
    ws.addEventListener("open", function() {
        const message = JSON.stringify({type: "join", uid})
        ws.send(message);
        wsMessageElement.value = wsMessageElement.value + `\nsent:\n ${message}\n`
    })
}

function receiveMoves(ws) {
    ws.addEventListener("message", function(message) {
        console.log(message.data)
        const event = JSON.parse(message.data)
        wsMessageElement.value = wsMessageElement.value + `\nreceived:\n ${message.data}\n`
        console.log('message.data.type:', event.type);
        switch (event.type) {
            case "join_success":
                gameState = event.game_state;
                boardArray = event.board;
                if (event.game_status === "waiting") {
                    side = "white";
                } else {
                    side = event.side;
                } 

                if (side == "white" && event.game_status === "ready") {
                    myTurn = true;
                } else {
                    board = new Chessboard(
                        document.getElementById("board"),
                        {
                            position: FEN.start,
                            orientation: side[0],
                        },
                    );
                }
                if (myTurn) sendMoves(ws);
                // window.board = board

                console.log('boardArray:', boardArray);
                break;
            case "move":
                console.log(event);
                const move = event.move;
                board.movePiece(move.src, move.dest, true) // `true` is for 'animated'
                  .then(something => console.log(something));
                gameState = event.game_state;
                boardArray = event.board;
                console.log('updated gameState and boardArray');
                myTurn = true;
                sendMoves(ws);
        }
        // TODO: in a case statement,
        //   if it's a move from a player other than this one, use `ground.move("a4", "a5")`
    }) 
}

function sendMoves(ws) {
    if (!myTurn) {
        board.disableMoveInput();
    } else {
        board.enableMoveInput(function (event) {
            switch (event.type) {
            case INPUT_EVENT_TYPE.moveInputStarted:
              // return `true`, if input is accepted/valid, `false` aborts the interaction, the piece will not move
              return true
            case INPUT_EVENT_TYPE.validateMoveInput:
              // return true, if input is accepted/valid, `false` takes the move back
              const msg = JSON.stringify({
                uid,
                type: "move",
                src: event.squareFrom,
                dest: event.squareTo,
                piece: getPieceAt(event.squareFrom),
                capture: getPieceAt(event.squareTo) ? 1 : 0,
              })
              ws.send(msg)
              wsMessageElement.value = wsMessageElement.value + `\nsent:\n ${msg}\n`
              myTurn = false;
              board.disableMoveInput();
              return true
            case INPUT_EVENT_TYPE.moveInputCanceled:
              console.log(`moveInputCanceled`)
          }
       }, side === "black" ? COLOR.black : COLOR.white)
    }
}

let squareToIndex = {}
let counter = 0
for (let file of Array.from("abcdefgh")) {
    for (let rank of Array.from("12345678")) {
            squareToIndex[`${file}${rank}`] = counter;
            counter++;
        }
    }

function getPieceAt(src) {
    const idx = squareToIndex[src];
    const piece = boardArray[idx];
    return piece
}
