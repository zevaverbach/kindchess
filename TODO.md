# Bugs
- [x] can't click on a space if you're hovering over the blue dot
- [x] if you click an ineligible square (no dots) after selecting a piece, 
      it doesn't remove the dots but it un-highlights the piece and makes it so you can't click on a dot to move the piece

# Front End
- [x] disable pinch to zoom
- [ ] "your turn"
- [ ] make room for non-game-over messages, use colors
- [ ] use promotion dialog that's built into cm-chessboard
- [ ] build out the site, make it look nice
  - [ ] nav bar
- [ ] change title when game is over
- [x] add ethical analytics
- [x] maybe get rid of the 'share url' button altogether
- [x] make the 'create game' button bigger on mobile

# Features
- [ ] A player who has offered a draw shall not, 
      before completing a further six moves be entitled to make another offer. 
- [ ] No player shall be entitled to offer more than three draws in any one game.
- [ ] enable reconnecting instead of 'abandoned' when you leave
  - [ ] use cookies for each game
  - [ ] deliver the HTML + JS with the current state of the game when getting a reconnect request
- [ ] anonymous matchups
- [ ] move history
- [ ] stockfish
- [ ] some basic rate limiting/IP-banning
- [ ] game clock
  - [ ] need to send an 'ack'(knowledged) message when the curernt player receives the previous move of the other player
- [ ] material tracking - points, pieces
  - consider using [these web components](https://shoelace.style/) for straightforward, buildless dev.
- [ ] accounts/auth [link](https://websockets.readthedocs.io/en/10.4/topics/authentication.html#sending-credentials)
- [ ] enforce move limit (draw)

# Optimization
- [ ] add some kind of analytics/logging
  - [ ] number of concurrent games
  - [ ] memory usage with alerts
- [ ] load testing
- [ ] find shortcuts to limit computation, storage, and bytes over the wire
  - [ ] profile the running code
    - [ ] number of computations for each move
    - [ ] how long does it take to process a move?
  - [ ] any advantage in pub/sub (redis) for games?
  - [ ] cache possible moves for every board
    - [ ] look in this cache before trying to calculate
  - [ ] persist/serialize the board differently
    - instead of FEN, maybe a hash
    - [bitboard](https://blog.devgenius.io/improve-as-a-software-engineer-by-writing-a-chess-engine-c360109371aa)
      - there are bit operations in redis, si jamais
  - [ ] use a CDN
