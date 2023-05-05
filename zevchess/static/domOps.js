import {
    MARKER_TYPE
} from './node_modules/cm-chessboard/src/cm-chessboard/Chessboard.js';

import {
    store
} from './store.js';

const messageBox = document.getElementById('messagebox');
const buttonDrawOffer = document.getElementById('draw-button');
buttonDrawOffer.addEventListener('click', event => {
    event.preventDefault();
    document.dispatchEvent(new CustomEvent('drawOffer', {
        detail: {
            message: {
                source: 'self'
            },
        },
    }));
})

const buttonDrawAccept = document.getElementById('draw-accept-button');
buttonDrawAccept.addEventListener('click', event => {
    event.preventDefault();
    document.dispatchEvent(new CustomEvent('drawAccept'));
})

const buttonDrawReject = document.getElementById('draw-reject-button');
buttonDrawReject.addEventListener('click', event => {
    event.preventDefault();
    document.dispatchEvent(new CustomEvent('drawReject', {
        detail: {
            message: {
                source: 'self'
            },
        },
    }));
})

const buttonDrawWithdraw = document.getElementById('draw-withdraw-button');
buttonDrawWithdraw.addEventListener('click', event => {
    event.preventDefault();
    document.dispatchEvent(new CustomEvent('drawWithdraw', {
        detail: {
            message: {
                source: 'self'
            },
        },
    }));
});

document.addEventListener('drawOffer', event => {
    const message = event.detail.message;
    if (message.source === 'self') {
        store.ws.send(JSON.stringify({
            'uid': store.uid,
            type: "draw",
            draw: "offer"
        }));
        buttonDrawOffer.style.display = 'none';
        buttonDrawWithdraw.style.display = 'inline';
        displayMessage("you have offered a draw.");
        store.selfDrawOffer = true;
        store.canOfferDraw = false;
    } else if (message.source === 'other') {
        displayMessage(message.message);
        buttonDrawOffer.style.display = 'none';
        buttonDrawAccept.style.display = 'inline';
        buttonDrawReject.style.display = 'inline';
        store.otherDrawOffer = true;
    }
})


document.addEventListener('drawWithdraw', event => {
    if (event.detail.message.source === 'self') {
        buttonDrawWithdraw.style.display = 'none';
        store.ws.send(JSON.stringify({
            'uid': store.uid,
            type: "draw",
            draw: "withdraw"
        }));
        store.selfDrawOffer = false;
    } else {
        buttonDrawAccept.style.display = 'none';
        buttonDrawReject.style.display = 'none';
        clearMessage();
        displayMessage(event.detail.message.message, false);
        if (store.canOfferDraw) {
            buttonDrawOffer.style.display = 'inline';
        }
        store.otherDrawOffer = false;
    }
})



document.addEventListener('drawReject', event => {
    const message = event.detail.message;
    if (message.source === 'self') {
        clearMessage();
        buttonDrawAccept.style.display = 'none';
        buttonDrawReject.style.display = 'none';
        if (store.canOfferDraw) {
            buttonDrawOffer.style.display = 'inline';
        }
        store.ws.send(JSON.stringify({
            'uid': store.uid,
            type: "draw",
            draw: "reject"
        }));
        store.otherDrawOffer = false;
    } else {
        buttonDrawWithdraw.style.display = 'none';
        clearMessage();
        displayMessage(message.message);
        store.selfDrawOffer = false;
    }
})



document.addEventListener('drawAccept', _ => {
    buttonDrawAccept.style.display = 'none';
    buttonDrawReject.style.display = 'none';
    store.ws.send(JSON.stringify({
        'uid': store.uid,
        type: "draw",
        draw: "accept"
    }));
})

document.addEventListener('drawWithdraw', event => {
    const message = event.detail.message;
    if (message.source === 'self') {
        buttonDrawWithdraw.style.display = 'none';
    } else {
        buttonDrawAccept.style.display = 'none';
        buttonDrawReject.style.display = 'none';
        clearMessage();
        displayMessage(message.message);
        if (store.canOfferDraw) {
            buttonDrawOffer.style.display = 'inline';
        }
    }
});


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
    messageBox.innerHTML = message;
    clearTimeout(store.pendingTimeout);
    if (timeout) {
        store.pendingTimeout = setTimeout(function() {
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
    messageBox.innerHTML = "";
}

export function showResignButton() {
    let btn = document.getElementById('resign-button');
    btn.style.display = "inline";
    btn.addEventListener('click', () => {
        store.ws.send(JSON.stringify({
            'uid': store.uid,
            type: "resign"
        }));
    })
}

export function showDrawButton() {
    if (buttonDrawOffer.style.display == 'none') {
        buttonDrawOffer.style.display = 'inline';
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
    hideDrawOfferButton();
    document.getElementById('resign-button').style.display = 'none';
}

export function hideDrawOfferButton() {
    try {
        drawOfferButton.style.display = 'none';
    } catch {
        return null;
    }
}
export function hideDrawAcceptAndRejectButtons() {
    buttonDrawAccept.style.display = 'none';
    buttonDrawReject.style.display = 'none';
}

export function showDrawAcceptAndRejectButtons() {
    buttonDrawAccept.style.display = 'inline';
    buttonDrawReject.style.display = 'inline';
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
