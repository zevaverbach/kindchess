- websocket API
  - [x] wrong number of watchers is shown once someone leaves (seems like it's not always decrement, or else maybe it's including the players once there's been more than one watcher?)
  - [x] "someone has left chat" is the message shown when a watcher leaves! (also wrong count)
  - [x] send entire game state at start of game, including to players
  - [x] who abandoned the game? there's some confusion here
    - "black abandoned the game, so white wins!" -- this happens when white abandons

- [ ] create a basic web interface
  - [x] /
    - [x] when you click on the create game button it automatically brings you to that new URL
    - [x] list of active games, each joinable
  - [ ] /<uid>
    - [x] render the board
    - [x] use [cm-chessboard][3] which has event handlers
    - [x] connect the board!
        - [x] when a piece moves, trigger a ws message
        - [x] freeze the pieces when it's not that player's turn
        - [x] turn the board around for black
          - [x] get which player the ws is for, set that as a global var
    - [x] only allow legal moves
      - [x] check possible_moves as delivered with 'your_turn' event
      - [x] check castling (what does that look like from the board, 'o-o' or?
    - [ ] support castling
       - [ ] move the rook automatically
       - [ ] deliver the move accurately to the server
       - [ ] make sure it's shown on opponent's/watchers' boards
    - [x] make captures work (have to deliver 'capture' arg to ws server)
    - [ ] show the allowed moves  [link][4]
    - [ ] indicate checkmate
    - [ ] indicate check
    - [ ] show previous move coloring
    - [ ] show what players/watchers are there
    - [x] connect to websocket server
    - [x] 'invite' button which copies the URL to your clipboard
    - [x] a debug box to show the websocket messages getting sent/received
  - [ ] when a game is over, keep the page stable even though the websocket connection is closed
    - [ ] alternatively, don't close the websocket connection so chat can continue

[1]: https://websockets.readthedocs.io/en/stable/intro/index.html
[2]: https://websockets.readthedocs.io/en/stable/topics/authentication.html
[3]: https://github.com/shaack/cm-chessboard#enablemoveinputeventhandler-color--undefined
[4]: https://shaack.com/projekte/cm-chessboard/examples/validate-moves.html
