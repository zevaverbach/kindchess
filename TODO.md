
- [x] create a basic web API
  - [x] HTTP
    - [x] /game
      - [x] POST
         - [x] /create
  - [ ] websockets
     - [x] there's a bug (Feb 5, 2023) where some invalid chars are sent but a) somehow this doesn't produce an error and 'continue' and b) the sender gets disconnected. Possibly I just fat-fingered this and disconnected myself, BUT the game didn't get set as "abandoned" when it happened, which points to an actual bug.
        - resolved on Feb 6, 2023 with commit c510c4f51e61c0b4a555016bf70de46056391837
     - [x] use the [websockets][1] library, at first without concerning yourself with authentication
     - [ ] events
         - [x] handle abandoned games
           - [x] remove from redis, (maybe) add to db
         - [x] join
         - [x] resign
         - [ ] draw
            - [ ] requested
                - [ ] this has to be implemented similarly to pawn promotion in core
            - [x] accepted 
         - [x] move
            - [x] try stalemate
            - [x] try the fool's mate, make sure it goes
                - f2-f3, e7-e5, g2-g4, Qd8-Qh4
            - [x] on success, return to whoever's turn it is
                - [x] all possible moves
                - [x] new game state
                - [x] from/to of prev move
            - [x] don't allow someone to make a move who isn't attached to a game! (different UID)
            - [x] say "it's your turn" to whoever's turn it is, i guess as a separate message
            - [x] provide the game state to new watchers
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
