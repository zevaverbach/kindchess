# Purpose
A chess server built from scratch (except the board itself). It supports playing via web browser, 
and later it will be playable via command line/TUI or messaging.

I'm interested in this because a) I like chess and b) I want to learn more about system design and
related topics.

# Requirements

## Production
- a Redis server 
- a Postgres instance
- Python 3.11
- `./requirements.txt`

## Development 
- all of the above, substituting `requirements-dev.txt` for `requirements.txt`.
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

# Deployment

## New Service/Infra
- create the service in render.com dashboard
  - associate the appropriate env group (`zevchess` or `zevchess-dev`)
  - use the default `pip install -r requirements.txt`
  - for web API, `gunicorn -w 2 <or however many> app:application`
  - for websocket server, `python ws_server.py`
  - run `python init_db.py`
    - this could be run locally if you tell it the appropriate DB to connect to

## Code Updates
- simply push to the monorepo, then either wait 1-10 mins to mirror to Github or manually sync (https://code.averba.ch/Zev/zevchess/settings)


# Testing
- load testing (TODO as of March 3 2023)
- unit testing (in process via test-driven development)

# Cost
- $32/month as of feb 27 2023
  - postgres $7 (dev $0)
  - redis $10 (dev $0)
  - websocket server $7 (dev $0)
  - web API server $7 (dev $0)

# Roadmap
Once there's a functional, not-too-buggy web API and web client, I'll load test and profile it 
to see what might be optimized. When nearing the "end of the road" of optimizations in Python, 
I'll explore porting to another language.

My initial thought has been to port it to Go, but it looks like for websockets there are some 
better-performing choices:

Node, [Bun](https://twitter.com/jarredsumner/status/1562121275945803776?lang=en) or even 
[socketify](https://raw.githubusercontent.com/cirospaciari/socketify.py/main/misc/ws-bar-graph.png) 
seem like great choices as they're able to send hundreds of thousands of messages per second.

I'm excited about writing it in a language other than Python, though, and I'm wondering if 
the gains in websocket performance will be offset by the slowness of the engine. 

The point here is "the journey", as I want to learn to measure and improve performance, 
including strategies beyond code.

# UX
- super low-friction to jumping into a game with people you know, or maybe who are part of a trusted group
- friendliness, zero tolerance for jerks

# UI 
- super minimal, fewer widgets than chess.com/lichess
- emphasis on socializing, including voice
- thoughtful chess playing, possibly including an optional "minimum time to move"
- ability to jump ahead and imagine moves by both sides while a) waiting for opponent to move or b) figuring out how to move.
  - store moves in a list and choose from them when ready
    - only for the very next move at first, not multiple

# Resources Used
- [generate FEN from board](http://www.netreal.de/Forsyth-Edwards-Notation/index.php)
- [generate board from FEN](http://www.ee.unb.ca/cgi-bin/tervo/fen.pl)
- [the board](https://github.com/shaack/cm-chessboard)
