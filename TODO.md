
- [ ] create a basic web API
  - [x] HTTP
    - [x] /game
      - [x] POST
         - [x] /create
  - [ ] websockets
     - [x] use the [websockets][1] library, at first without concerning yourself with authentication
     - [ ] events
         - [ ] handle abandoned games
           - [ ] remove from redis, (maybe) add to db
         - [x] join
         - [ ] resign
         - [ ] draw
         - [ ] move

- [ ] create a basic web interface
  - [ ] no user registration or chat
  - [ ] whoever creates the game is player 1
  - [ ] the second to arrive to the game is player 2
  - [ ] everyone else is a spectator

- [ ] [add authentication][2] to websockets
  - preferably not user/pass at first, just a way to make sure it's the same client session every move

[1]: https://websockets.readthedocs.io/en/stable/intro/index.html
[2]: https://websockets.readthedocs.io/en/stable/topics/authentication.html
