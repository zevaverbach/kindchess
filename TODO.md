# Bugs

# small UI improvements
- [x] shade the selected piece/background
- [x] show previous move coloring
- [ ] change color of target piece when it's in the path of the selected piece 
  - [ ] instead of a dot
- [ ] support landscape mode on mobile (fill the screen ,no scrolling)
- [ ] add instructions for inviting a friend
- [ ] add a spinner when creating a game
- [x] make dots smaller
- [ ] don't show the actual UIDs on the main screen, if at all
- [ ] gray out the board when the game is over for a reason other than checkmate/stalemate
  - [ ] or some other visual indication (8-bit GAME OVER?)

# Next
- [x] make sure same-origin policy is getting enforced
- [ ] some basic rate limiting/IP-banning
  - [ ] alternatively, require invites to actually use it, with shareable invite codes
- [ ] add a feedback box
- [ ] add a newsletter signup
- [x] put it at a domain, even if it's averba.ch/chess
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
- [ ] move history
- [ ] accounts/auth [link](https://websockets.readthedocs.io/en/10.4/topics/authentication.html#sending-credentials)
- [ ] figure out how to get the message to actually display when being warned about abandoning a game.
- [ ] dark mode

