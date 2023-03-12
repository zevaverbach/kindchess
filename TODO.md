# Bugs
- [x] pawn promotion needs to be rewritten
  - [x] the pawn can't transform into its promotion piece _before_ moving to its destination square,
    it messed up get_possible_moves

# Features
- [x] initiate closing of connection from client (it's not getting called on the server currently)
- [x] resign
- [x] draw
  - [x] don't allow it until both sides have moved
  - [x] change message sent from server for
    - [x] reject
    - [x] accept
  - [x] hide 'offer draw' and show 'withdraw draw' when there's a pending one from self
  - [x] make a dialog for accepting/rejecting a draw
     - made buttons instead
  - [x] erase 'you have offered a draw' when it's been rejected or the other person has moved
  - [x] bug: when white offers a draw, white's buttons are changed instead of black's (from 'offer' to 'accept' and 'decline')
- [ ] threefold repetition
  - same position
  - same person's turn as two other occurrences
  - same en passant state
  - same castling state
  - NOT automatic, must be requested by either player _before_ the next move is made

# small UI improvements
- [ ] gray out the board when the game is over for a reason other than checkmate/stalemate
  - [ ] or some other visual indication (8-bit GAME OVER?)
- [ ] shade the selected piece/background
- [ ] show previous move coloring
- [ ] don't show the actual UIDs on the main screen, if at all
- [ ] add instructions for inviting a friend
- [ ] add a spinner when creating a game
- [ ] make dots smaller
- [ ] put dots in front of pieces (z-index)


# Next
- [ ] put it at a domain, even if it's averba.ch/chess
- [ ] make "private room" functionality where you can create a room and it's always available
  - [ ] allow room owner to put name tags on for both players
- [ ] load testing
- [ ] add some kind of analytics/logging
  - [ ] number of concurrent games
  - [ ] memory usage with alerts
- [ ] find shortcuts to limit computation and storage
  - [ ] profile the running code
    - [ ] number of computations for each move
    - [ ] how long does it take to process a move?
  - [ ] any advantage in pub/sub for games?
  - [ ] cache possible moves for every board
    - [ ] look in this cache before trying to calculate
  - [ ] persist/serialize the board differently
    - instead of FEN, maybe a hash
    - [bitboard](https://blog.devgenius.io/improve-as-a-software-engineer-by-writing-a-chess-engine-c360109371aa)
      - there are bit operations in redis, si jamais
- [ ] game clock
- [ ] material tracking - points, pieces
- [ ] build out the site, make it look nice
  - consider using [these web components][3] for straightforward, buildless dev.
- [ ] move history
  - [ ] make sure it gets captured even when the game moves into a buggy state
  - [ ] make a way to grab it from DB/redis and provide it to the front end
  - [ ] make a way of showing/walking through history on front end
  - [ ] make a way to walk through a bunch of pre-determined moves for testing purposes
- [ ] accounts/auth
- [ ] figure out how to get the message to actually display when being warned about abandoning a game.
- [ ] dark mode

[3]: https://shoelace.style/
