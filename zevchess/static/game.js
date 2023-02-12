import { Chessground } from "./chessground.min.js";

const config = {};
const ground = Chessground(document.getElementById('chessground'), config);

const numberOfWatchers = 0;
const players = {
    black: null,
    white: null,
}
const gameState = {}
const uid = window.location.pathname.replace('/', '');

const wsMessageElement = document.getElementById('ws');

window.addEventListener("DOMContentLoaded", () => {
    const board = document.getElementById("chessground");
    const ws = new WebSocket("ws://localhost:8001/");
    joinGame(ws);
    receiveMoves(board, ws);
    sendMoves(board, ws);
})

function joinGame(ws) {
    ws.addEventListener("open", function() {
        const message = JSON.stringify({type: "join", uid})
        ws.send(message);
        wsMessageElement.value = wsMessageElement.value + `\nsent: ${message}\n`
    })
}

function receiveMoves(board, ws) {
    ws.addEventListener("message", function(message) {
        console.log(message.data)
        const event = JSON.parse(message.data)
        wsMessageElement.value = wsMessageElement.value + `\nreceived: ${message.data}\n`
        // TODO: in a case statement,
        //   if it's a move from a player other than this one, use `ground.move("a4", "a5")`
    }) 
}

function sendMoves(board, ws) {
    return null;
}
