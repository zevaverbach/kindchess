# Bugs

# Features
- [ ] limits to draw offers
    - [x] A player who has offered a draw shall not, before completing a further six moves be entitled to make another offer. 
    - [x] No player shall be entitled to offer more than three draws in any one game.
    - [x] bug: black can't offer a draw until after -three- half moves, should be two
    - [ ] bug: black's 'offer draw' button disappears after rejecting a draw offer from white
      - ONLY when white's offer was sent during white's turn
      - ONLY in the first couple moves
    - [ ] bug: black's 'offer draw' button reappears after white rejects a draw offer
      - ONLY when black's offer was sent during black's turn
      - if you do it a second time, the 'offer draw' won't reapear
- [ ] brief instructions in 'waiting for black to join' modal about sharing the game URL
- [ ] make "page doesnt exist html
- [ ] revert coloring of recent move squares so that white and black squares are differentiated
- [ ] enable reconnecting instead of 'abandoned' when you leave
  - [ ] use SocketIO, it includes reconnecting
- [ ] anonymous matchups
- [ ] move history
- [ ] use promotion dialog that's built into cm-chessboard
- [ ] build out the site, make it look nice
  - [ ] nav bar
- [ ] stockfish
- [ ] some basic rate limiting/IP-banning
- [ ] game clock
  - [ ] need to send an 'ack'(knowledged) message when the curernt player receives the previous move of the other player
- [ ] material tracking - points, pieces
  - consider using [these web components](https://shoelace.style/) for straightforward, buildless dev.
- [ ] accounts/auth [link](https://websockets.readthedocs.io/en/10.4/topics/authentication.html#sending-credentials)
- [ ] enforce move limit (draw)

# Deployment
- [ ] create `init_db_prod.py` script 
- [ ] incorporate alembic and start doing DB migrations when there's a schema change
- [ ] ideally, detect if there's a change to `ztypes.GameState.to_db_dict`'s keys without a corresponding migration

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
