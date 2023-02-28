# Purpose
I want to build a chess application from scratch. It will be an API-first monolith that supports playing via

1) web browser
2) command line/TUI
3) messaging

I'm interested in this because a) I like chess and b) I want to learn more about system design.

# Requirements

## Production
- a Redis server 
- sqlite3
- Python 3.11
- ./requirements.txt

## Development (requirements-dev.txt)

Everything from above plus
  - pylint
  - ipython
  - pytest
  - pyperclip
  - python-lsp-server[all]
  - `websocat` or another websocket client (`> brew install websocat`)
    - for testing: `> websocat localhost:8001`

## Environment Variables
- DB_USER
- DB_PASS
- DB_NAME
- DB_HOSTNAME
- DB_URL
- DB_URL_PUBLIC
- PSQL_COMMAND
- REDIS_NAME
- REDIS_URL
- ZEVCHESS_PROD (0/1)


# Testing
- load testing (TODO)
- unit testing (in process via test-driven development)

# Deployment
- v1 will be via render.com with some auto-scaling
- the DB will have to be switched/refactored for scaling, since it's file-based and currently living on (each) server

## Cost
- $32 as of feb 27 2023
  - postgres $7 (dev $0)
  - redis $10 (dev $0)
  - websocket server $7 (dev $0)
  - web API server $7 (dev $0)

## Services

### websocket server

### web API server


# UI Principles
- super minimal, fewer widgets than chess.com/lichess
- emphasis on socializing, including voice

# Roadmap
Once there's a functional, not-too-buggy web API and web client, I'll load test and profile it to see what might be optimized. When nearing the "end of the road" of optimizations in Python, I'll explore porting to another language.

My initial thought has been to port it to Go, but it looks like for websockets there are some better-performing choices:

Node, [Bun](https://twitter.com/jarredsumner/status/1562121275945803776?lang=en) or even [socketify](https://raw.githubusercontent.com/cirospaciari/socketify.py/main/misc/ws-bar-graph.png) seem like great choices as they're able to send hundreds of thousands of messages per second.

I'm excited about writing it in a language other than Python, though, and I'm wondering if the gains in websocket performance will be offset by the slowness of the engine. 

The point here is "the journey", as I want to learn to measure and improve performance, including strategies beyond code.

# UX
- super low-friction to jumping into a game with people you know, or maybe who are part of a trusted group
- ability to jump ahead and imagine moves by both sides while a) waiting for opponent to move or b) figuring out how to move.
  - store moves in a list and choose from them when ready
    - only for the very next move at first, not multiple

# Resources Used
- [generate FEN from board](http://www.netreal.de/Forsyth-Edwards-Notation/index.php)
- [generate board from FEN](http://www.ee.unb.ca/cgi-bin/tervo/fen.pl)
- [the board](https://github.com/shaack/cm-chessboard)

# Prior Art
- [glee](https://github.com/tonyOreglia/glee)
  - check out [the "bitboard" idea](https://blog.devgenius.io/improve-as-a-software-engineer-by-writing-a-chess-engine-c360109371aa) as a possible optimization
- [FEN validation](https://chess.stackexchange.com/a/1483/34173)
