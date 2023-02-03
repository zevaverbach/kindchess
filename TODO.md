
- [ ] create a basic web API
  - [x] HTTP
    - [x] /game
      - [x] POST
         - [x] /create
  - [ ] websockets
     - [x] use the [websockets][1] library, at first without concerning yourself with authentication
     - [ ] set up a test framework
        - [ ] create a game, get UID
        - [ ] do moves 'til it's checkmate, make sure that happens
     - [ ] events
         - [ ] handle abandoned games
           - [ ] remove from redis, (maybe) add to db
            - [ ] end game when a player closes connection: `ws.wait_closed()`
         - [x] join
         - [ ] resign
         - [ ] draw
         - [ ] move
            - [ ] don't just send new game state, send 'move' so it can be animated
            - [ ] return all possible moves
            - [ ] don't allow if there's only one player
            - [ ] don't allow if the game is over
            - [ ] don't allow a player to move out of turn
            - [ ] don't allow a spectator to make a move
            - [ ] don't allow someone to make a move who isn't attached to a game! (different UID)

- [ ] create a basic web interface
  - [ ] no user registration or chat
  - [ ] whoever creates the game is player 1
  - [ ] the second to arrive to the game is player 2
  - [ ] everyone else is a spectator

- [ ] [add authentication][2] to websockets
  - preferably not user/pass at first, just a way to make sure it's the same client session every move

[1]: https://websockets.readthedocs.io/en/stable/intro/index.html
[2]: https://websockets.readthedocs.io/en/stable/topics/authentication.html
