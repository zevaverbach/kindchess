- [ ] pawn promotion! (websockets and web view)
  - maybe use native `dialog` [link](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/dialog)
- [ ] threefold repetition

# small UI improvements
  - [ ] shade the selected piece/background
  - [ ] don't show the actual UIDs on the main screen, if at all
  - [ ] add instructions for inviting a friend

# Bugs
  - [ ] when 'abandoning' the game, that side's king gets highlighted in red
  - [ ] there's a bunch of stray UIDs on the home screen, they're getting stuck in Redis 
  - [ ] why does the checkmated player automatically disconnect?
    - it currently causes a "white abandoned the game" message which has to be ignored on the front end
  - [ ] there are still various errors showing in the log

# Next
- [ ] put it at a domain, even if it's averba.ch/chess
- [ ] add ethical analytics
- [ ] load testing
- [ ] find shortcuts to limit computation and storage
  - [ ] cache possible moves for every board
    - [ ] look in this cache before trying to calculate
  - [ ] persist/serialize the board differently
    - instead of FEN, maybe a hash
    - [bitboard](https://blog.devgenius.io/improve-as-a-software-engineer-by-writing-a-chess-engine-c360109371aa)
  - [ ] if a pawn, king, knight is sufficiently far away, no need to check whether it can put the opposing king in check
- [ ] game clock
- [ ] material tracking - points, pieces
- [ ] build out the site, make it look nice
  - consider using [these web components][3] for straightforward, buildless dev.
- [ ] show previous move coloring
- [ ] move history
  - [ ] make sure it gets captured even when the game moves into a buggy state
  - [ ] make a way to grab it from DB/redis and provide it to the front end
  - [ ] make a way of showing/walking through history on front end
  - [ ] make a way to walk through a bunch of pre-determined moves for testing purposes
- [ ] accounts/auth
- [ ] figure out how to get the message to actually display when being warned about abandoning a game.
- [ ] don't warn about abandoning a game if the game is over
- [ ] show what players/watchers are there
