# Bugs

# small UI improvements
- [x] support landscape mode on mobile (fill the screen ,no scrolling)
- [x] make the board centered
- [x] make it so the buttons don't go off the page (board a bit smaller?)
- [ ] add a spinner when creating a game
- [ ] make the messages (game on, game over, etc.) modals which hover over the center of the board
- [x] make dots smaller
- [x] shade the selected piece/background
- [x] show previous move coloring
- [x] show dot on top of possbile target piece (possible moves)
  - z-index doesn't cut it for this so far

# Next
- [ ] enable reconnecting instead of 'abandoned' when you leave
- [ ] anonymous matchups
- [ ] move history
- [ ] stockfish
- [ ] add instructions
- [ ] some basic rate limiting/IP-banning
  - [ ] alternatively, require invites to actually use it, with shareable invite codes
- [ ] add a feedback box
- [ ] add a newsletter signup
- [ ] make "private room" functionality where you can create a room and it's always available
  - [ ] allow room owner to put name tags on for both players
  - [ ] what would be cool is chess.org/myname/friendname
- [ ] load testing
- [ ] add some kind of analytics/logging
  - [ ] number of concurrent games
  - [ ] memory usage with alerts
- [ ] find shortcuts to limit computation and storage
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
- [ ] game clock
- [ ] material tracking - points, pieces
- [ ] build out the site, make it look nice
  - consider using [these web components](https://shoelace.style/) for straightforward, buildless dev.
- [ ] accounts/auth [link](https://websockets.readthedocs.io/en/10.4/topics/authentication.html#sending-credentials)
- [ ] figure out how to get the message to actually display when being warned about abandoning a game.
- [ ] use promotion dialog that's built into cm-chessboard
- [ ] gray out the board when the game is over for a reason other than checkmate/stalemate
  - [ ] or some other visual indication (8-bit GAME OVER?)
- [ ] change color of target piece when it's in the path of the selected piece 
  - [ ] instead of a dot
- [ ] dark mode
- [x] put it at a domain, even if it's averba.ch/chess
- [x] make sure same-origin policy is getting enforced

