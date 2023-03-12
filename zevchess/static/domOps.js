export function showShareButton(main) {
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


