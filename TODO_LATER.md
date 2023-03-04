- [ ] enforce move limit (draw)
- [ ] allow refreshing of the browser without destroying the game
  - [ ] do lichess or chess.com allow this?
- [ ] make or find more tests
    - [ ] could it ever be illegal to make the same move as a pawn when it's promoting with another piece?
        - this is how the pawn promotion move is tested once the promotion piece type is chosen
- [ ] handoff from one UI to another
- [ ] organize code
  - [ ] core
      - [ ] pieces
      - [ ] ...
  - [ ] UIs
  - [ ] move the extra move validation out of websockets and into a separate interfaces module (not core)
    - [ ] "can't move for another player", "can't move when you're a spectator", etc.

[3]: https://shoelace.style/
