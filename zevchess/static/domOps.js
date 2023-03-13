import { MARKER_TYPE } from './node_modules/cm-chessboard/src/cm-chessboard/Chessboard.js';

export function displayMessage(message, timeout = true) {
  document.getElementById('messagebox').innerHTML = message;
  if (timeout) {
    setTimeout(function () {
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
  document.getElementById('messagebox').innerHTML = '';
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
      ws.send(JSON.stringify({uid, type: "resign"}));
    })
    btn.innerText = "Resign"
    document.getElementsByTagName('main')[0].appendChild(btn);
  }
}

export function showDrawButton(uid, displayMessage, ws, setSelfDrawOffer) {
  let btn = document.getElementById('draw-button');
  if (btn && btn.style.display === 'inline') return;
  if (btn) {
    btn.style.display = "inline";
  } else {
    btn = document.createElement("button");
    btn.id = "draw-button";
    btn.addEventListener('click', () => {
      ws.send(JSON.stringify({uid, type: "draw", draw: "offer"}));
      hideDrawButton();
      showWithdrawDrawButton(ws, uid);
      displayMessage("you have offered a draw.", false);
      setSelfDrawOffer(true);
    })
    btn.innerText = "Offer Draw"
    document.getElementsByTagName('main')[0].appendChild(btn);
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
      ws.send(JSON.stringify({uid, type: "draw", draw: "withdraw"}));
      hideWithdrawDrawButton();
      showDrawButton();
      clearMessage();
    })
    btn.innerText = "Withdraw Draw Offer"
    document.getElementsByTagName('main')[0].appendChild(btn);
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
      ws.send(JSON.stringify({uid, type: "draw", draw: "accept"}));
    })
    btn.innerText = "Accept Draw"
    document.getElementsByTagName('main')[0].appendChild(btn);
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
      ws.send(JSON.stringify({uid, type: "draw", draw: "reject"}));
      hideDrawAcceptAndRejectButtons();
      clearMessage();
      showDrawButton();
    })
    btn.innerText = "Reject Draw"
    document.getElementsByTagName('main')[0].appendChild(btn);
  }
}

export function hideDrawAcceptAndRejectButtons() {
  try {
  document.getElementById('draw-accept-button').style.display = 'none';
  document.getElementById('draw-reject-button').style.display = 'none';
  } catch {
  } return null;
}

export function hideShareButton() {
  document.getElementById('share-button').style.display = 'inline';
}

export function showShareButton(displayMessage) {
  if (document.getElementById('share-button')) return
  const url = window.location.href;
  const btn = document.createElement("button");
  btn.id = "share-button";
  btn.addEventListener('click', () => {
    navigator.clipboard.writeText(url);
    displayMessage(
      `I've copied the following to your clipboard: ${url}, 
       feel free to share it with whoever you want to play against. 
       I'll let you know when they've joined!`, true
      )    
  })
  btn.innerText = "share invite URL"
  document.getElementsByTagName('main')[0].appendChild(btn);
}

export function showStalemate(gameState) {
  for (const color of ["white", "black"]) {
    const selector = `[data-square="${gameState['king_square_' + color]}"]`;
    document.querySelector(selector).classList.add("stale");
  }
}

export function showCheckmate(winner, gameState) {
  const checkmatedKingSquare = winner === "black" ? gameState.king_square_white: gameState.king_square_black;
  const selector = `[data-square="${checkmatedKingSquare}"]`;
  document.querySelector(selector).classList.add("mate");
}

export function updateCheckStatus(gameState, alreadyCheckedKing, setCheckedKing) {
  if ([0, 1].includes(gameState.its_check)) {
    let checkedKing = gameState.its_check === 0 ? gameState.king_square_white: gameState.king_square_black;
    setCheckedKing(checkedKing);
    document.querySelector(`[data-square="${checkedKing}"]`).classList.add("check")
  } else if (alreadyCheckedKing) {
      const query = `[data-square="${alreadyCheckedKing}"]`
      document.querySelector(query).classList.remove("check")
      setCheckedKing("");
  }
}


