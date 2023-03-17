import { MARKER_TYPE } from './node_modules/cm-chessboard/src/cm-chessboard/Chessboard.js';

const modal = document.getElementById('modal');
modal.addEventListener('cancel', event => {
  event.preventDefault();
});

export function displayModal(message) {
  modal.innerHTML = message;
  modal.showModal();
}

export function hideModal() {
  modal.close();
}

export function displayMessage(message, timeout = true) {
  const messageBox = document.getElementById('messagebox');
  messageBox.innerHTML = message;
  if (timeout) {
    setTimeout(function() {
      clearMessage();
    }, 3000);
  }
}

export function highlightPrevMove(from, to, fromWas, toWas, setPrevMove, board) {
  setPrevMove(from, to);
  board.removeMarkers(MARKER_TYPE.squarePrevMove, fromWas);
  board.removeMarkers(MARKER_TYPE.squarePrevMove, toWas);
  board.addMarker(MARKER_TYPE.squarePrevMove, from);
  board.addMarker(MARKER_TYPE.squarePrevMove, to);
}

export function clearMessage() {
  const messageBox = document.getElementById('messagebox');
  messageBox.innerHTML = "";
}

export function showResignButton(uid, ws) {
  let btn = document.getElementById('resign-button');
  if (btn && btn.style.display === "inline") return;
  if (btn) {
    btn.style.display = "inline";
  } else {
    btn = document.createElement("button");
    btn.id = "resign-button";
    btn.addEventListener('click', () => {
      ws.send(JSON.stringify({ uid, type: "resign" }));
    })
    btn.innerText = "Resign"
    document.getElementById('buttons-container').appendChild(btn);
  }
}

export function showDrawButton(uid, ws, setSelfDrawOffer) {
  let btn = document.getElementById('draw-button');
  if (btn && btn.style.display === 'inline') return;
  if (btn) {
    btn.style.display = "inline";
  } else {
    btn = document.createElement("button");
    btn.id = "draw-button";
    btn.addEventListener('click', () => {
      ws.send(JSON.stringify({ uid, type: "draw", draw: "offer" }));
      hideDrawButton();
      showWithdrawDrawButton(ws, uid);
      displayMessage("you have offered a draw.", false);
      setSelfDrawOffer(true);
    })
    btn.innerText = "Offer Draw"
    document.getElementById('buttons-container').appendChild(btn);
  }
}

function showWithdrawDrawButton(ws, uid) {
  let btn = document.getElementById('draw-withdraw-button');
  if (btn && btn.style.display === 'inline') return;
  if (btn) {
    btn.style.display = "inline";
  } else {
    btn = document.createElement("button");
    btn.id = "draw-withdraw-button";
    btn.addEventListener('click', () => {
      ws.send(JSON.stringify({ uid, type: "draw", draw: "withdraw" }));
      hideWithdrawDrawButton();
      showDrawButton();
      clearMessage();
    })
    btn.innerText = "Withdraw Draw Offer"
    document.getElementById('buttons-container').appendChild(btn);
  }
}

export function hideWithdrawDrawButton() {
  try {
    document.getElementById('draw-withdraw-button').style.display = 'none';
  } catch {
    return null;
  }
}

export function hideButtons() {
  hideDrawAcceptAndRejectButtons();
  hideWithdrawDrawButton();
  hideDrawButton();
  hideResignButton();
}

export function hideDrawButton() {
  try {
    document.getElementById('draw-button').style.display = 'none';
  } catch {
    return null;
  }
}

function hideResignButton() {
  try {
    document.getElementById('resign-button').style.display = 'none';
  } catch {
    return null;
  }
}

export function showDrawAcceptAndRejectButtons(ws, uid) {
  showDrawAcceptButton(ws, uid);
  showDrawRejectButton(ws, uid);
}

function showDrawAcceptButton(ws, uid) {
  let btn = document.getElementById('draw-accept-button');
  if (btn && btn.style.display === 'inline') return;
  if (btn) {
    btn.style.display = "inline";
  } else {
    btn = document.createElement("button");
    btn.id = "draw-accept-button";
    btn.addEventListener('click', () => {
      ws.send(JSON.stringify({ uid, type: "draw", draw: "accept" }));
    })
    btn.innerText = "Accept Draw"
    document.getElementById('buttons-container').appendChild(btn);
  }
}

function showDrawRejectButton(ws, uid) {
  let btn = document.getElementById('draw-reject-button');
  if (btn && btn.style.display === 'inline') return;
  if (btn) {
    btn.style.display = "inline";
  } else {
    btn = document.createElement("button");
    btn.id = "draw-reject-button";
    btn.addEventListener('click', () => {
      ws.send(JSON.stringify({ uid, type: "draw", draw: "reject" }));
      hideDrawAcceptAndRejectButtons();
      clearMessage();
      showDrawButton();
    })
    btn.innerText = "Reject Draw"
    document.getElementById('buttons-container').appendChild(btn);
  }
}

export function hideDrawAcceptAndRejectButtons() {
  try {
    document.getElementById('draw-accept-button').style.display = 'none';
    document.getElementById('draw-reject-button').style.display = 'none';
  } catch {
  } return null;
}

export function showStalemate(gameState) {
  for (const color of ["white", "black"]) {
    const selector = `[data-square="${gameState['king_square_' + color]}"]`;
    document.querySelector(selector).classList.add("stale");
  }
}

export function showCheckmate(winner, gameState) {
  const checkmatedKingSquare = winner === "black" ? gameState.king_square_white : gameState.king_square_black;
  const selector = `[data-square="${checkmatedKingSquare}"]`;
  document.querySelector(selector).classList.add("mate");
}

export function updateCheckStatus(gameState, alreadyCheckedKing, setCheckedKing) {
  if ([0, 1].includes(gameState.its_check)) {
    let checkedKing = gameState.its_check === 0 ? gameState.king_square_white : gameState.king_square_black;
    setCheckedKing(checkedKing);
    document.querySelector(`[data-square="${checkedKing}"]`).classList.add("check")
  } else if (alreadyCheckedKing) {
    const query = `[data-square="${alreadyCheckedKing}"]`
    document.querySelector(query).classList.remove("check")
    setCheckedKing("");
  }
}


