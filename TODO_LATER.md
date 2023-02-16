- [ ] build out the site, make it look nice
  - consider using [these web components][3] for straightforward, buildless dev.
- [ ] move the extra move validation out of websockets and into a separate interfaces module (not core)
  - [ ] "can't move for another player", "can't move when you're a spectator", etc.
- [ ] allow refreshing of the browser without destroying the game
  - [ ] or just don't allow refreshing of the page, or do an 'alert' to tell them it will end the game
- [ ] organize code
  - [ ] core
      - [ ] pieces
      - [ ] ...
  - [ ] UIs
- [ ] load testing
- [ ] move history
- [ ] consider [socketify][1] for performance if you're going to stay with Python
- [ ] make or find more tests
    - [ ] could it ever be illegal to make the same move as a pawn when it's promoting with another piece?
        - this is how the pawn promotion move is tested once the promotion piece type is chosen
- [ ] find shortcuts to limit computation and storage
  - [ ] cache possible moves for every board
    - [ ] look in this cache before trying to calculate
  - [ ] persist/serialize the board differently
    - instead of FEN, maybe a hash
    - [bitboard](https://blog.devgenius.io/improve-as-a-software-engineer-by-writing-a-chess-engine-c360109371aa)
  - [ ] if a pawn, king, knight is sufficiently far away, no need to check whether it can put the opposing king in check
- [ ] game clock
- [ ] enforce move limit (draw)
- [ ] threefold repetition
- [ ] material tracking - points, pieces
- [ ] accounts/auth
- [ ] detect cheating
- [ ] consider using [this web][2] component for the board, it seems nice

[1]: https://docs.socketify.dev/websockets-backpressure.html
[2]: https://github.com/shaack/cm-chessboard
[3]: https://shoelace.style/
