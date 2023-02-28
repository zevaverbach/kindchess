- [ ] pawn promotion! (websockets and web view)
  - maybe use native `dialog` [link](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/dialog)
- [ ] move history
- [ ] make a way to walk through a bunch of pre-determined moves for testing purposes

# Bugs
  - [ ] BUG: this isn't checkmate?
    - ![screenshot](screenshots/should_be_checkmate.png)
    - i can't replicate it (test_make_move_bug_11)
  - [ ] BUG: when 'abandoning' the game, that side's king gets highlighted in red
  - [ ] BUG: there are a bunch of error messages on websocket server
    - [link](https://dashboard.render.com/web/srv-cfuuh9t3t39doaurs5q0/logs)
  - [ ] BUG: why does the checkmated player automatically disconnect?
    - it currently causes a "white abandoned the game" message which has to be ignored on the front end
  - [ ] BUG: on dev server it says 'game not found' when creating a new game
  - [ ] BUG: there's a bunch of stray UIDs on the home screen, they're getting stuck in Redis 
  - [x] BUG: white king can't capture rook here??
    - ![screenshot](white_king_cant_capture_rook_BUG.png)
    - related: ![white rook doesn't exist after castling](white_rook_doesnt_exist_after_castling_BUG.png)
  - [x] BUG: this isn't check??
    - ![screenshot](screenshots/this_isnt_check_but_should_be_BUG.png)
    - ![screenshot](screenshots/this_isnt_check_but_should_be_BUG_2.png)

# small UI improvements
  - [ ] show the allowed moves [link][4]
  - [x] indicate checkmate
  - [x] indicate check
  - [x] indicate stalemate
  - [ ] show what players/watchers are there
[4]: https://shaack.com/projekte/cm-chessboard/examples/validate-moves.html
