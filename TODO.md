- core
  - [ ] mark 'winner' field of game state when there's a resignation

- [ ] create a basic web interface
  - [ ] /
    - [ ] 'create game' button
    - [ ] list of active games, each joinable
  - [ ] /<uid>
    - [ ] render the board
    - [ ] show what players/watchers are there
    - [ ] connect to websocket server
    - [ ] 'invite' button which copies the URL to your clipboard
  - [ ] when a game is over, keep the page stable even though the websocket connection is closed
    - [ ] alternatively, don't close the websocket connection so chat can continue

[1]: https://websockets.readthedocs.io/en/stable/intro/index.html
[2]: https://websockets.readthedocs.io/en/stable/topics/authentication.html
