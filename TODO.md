
- [ ] create a basic web API
  - [x] HTTP
    - [x] /game
      - [x] POST
         - [x] /create
  - [ ] websockets
     - [x] use the [websockets][1] library, at first without concerning yourself with authentication
     - [ ] move the extra move validation out of websockets and into core
        - [ ] "can't move for another player", "can't move when you're a spectator", etc.
     - [ ] set up a test framework
        - [ ] create a game, get UID
        - [ ] do moves 'til it's checkmate, make sure that happens
     - [ ] events
         - [x] handle abandoned games
           - [x] remove from redis, (maybe) add to db
         - [x] join
         - [ ] resign
         - [ ] draw
            - [ ] this has to be implemented similarly to pawn promotion in core
         - [ ] move
            - [ ] on success, return 
                - [ ] all possible moves
                - [ ] new game state
            - [ ] don't allow someone to make a move who isn't attached to a game! (different UID)
            - [ ] say "it's your turn" to whoever's turn it is, i guess as a separate message
            - [x] don't allow a websocket connection to 'join' a game if it already has joined one
            - [x] don't allow if there's only one player
            - [x] don't allow if the game is over
            - [x] don't allow a player to move out of turn
            - [x] don't allow a spectator to make a move

- [ ] create a basic web interface
  - [ ] no user registration or chat
  - [ ] whoever creates the game is player 1
  - [ ] the second to arrive to the game is player 2
  - [ ] everyone else is a spectator
  - [ ] when a game is over, keep the page stable even though the websocket connection is closed
    - [ ] alternatively, don't close the websocket connection so chat can continue

- [ ] [add authentication][2] to websockets
  - preferably not user/pass at first, just a way to make sure it's the same client session every move

[1]: https://websockets.readthedocs.io/en/stable/intro/index.html
[2]: https://websockets.readthedocs.io/en/stable/topics/authentication.html
