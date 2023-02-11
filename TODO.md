- core
  - [ ] mark 'winner' field of game state when there's a resignation
  - [ ] update 'existing_uids' redis list as games end
  - [ ] BUG: when leaving/refreshing the browser, the game gets removed but somehow remains as a link on the home screen
    - this might be because of the bullet point above
- websocket API
  - [ ] wrong number of watchers is shown once someone leaves (seems like it's not always decrement, or else maybe it's including the players once there's been more than one watcher?)
  - [ ] "someone has left chat" is the message shown when a watcher leaves! (also wrong count)
  - [ ] send entire game state at start of game

- [ ] create a basic web interface
  - [ ] /
    - [x] 'create game' button
    - [ ] when you click on the create game button it automatically brings you to that new URL
    - [x] list of active games, each joinable
  - [ ] /<uid>
    - [x] render the board
    - [ ] connect the board!
        - [ ] when a piece moves, trigger a ws message
    - [ ] show what players/watchers are there
    - [x] connect to websocket server
    - [ ] 'invite' button which copies the URL to your clipboard
    - [x] a debug box to show the websocket messages getting sent/received
  - [ ] when a game is over, keep the page stable even though the websocket connection is closed
    - [ ] alternatively, don't close the websocket connection so chat can continue

[1]: https://websockets.readthedocs.io/en/stable/intro/index.html
[2]: https://websockets.readthedocs.io/en/stable/topics/authentication.html
