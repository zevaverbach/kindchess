# Purpose
I want to build a chess application from scratch. It will be an API-first monolith that supports playing via

1) web browser
2) command line/TUI
3) messaging

I'm interested in this because a) I like chess and b) I want to learn more about system design.

# Requirements
- a Redis server 
- sqlite3
- Python 3.11
- ./requirements.txt
  - don't actually need in production (maybe switch to a more modern packager)
    - pylint
    - ipython
    - pytest

# Testing
- load testing (TODO)
- unit testing (in process via test-driven development)

# Deployment
- v1 will be via render.com with some auto-scaling

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
- stickers
- in-person chess 'dating'
- ability to flag moves in real-time or in retrospect
  - not sure it was good
  - this was probably good
  - blunder (retrospect only)

# Resources Used
- [generate FEN from board](http://www.netreal.de/Forsyth-Edwards-Notation/index.php)
- [generate board from FEN](http://www.ee.unb.ca/cgi-bin/tervo/fen.pl)

# Prior Art
- [glee](https://github.com/tonyOreglia/glee)
  - check out [the "bitboard" idea](https://blog.devgenius.io/improve-as-a-software-engineer-by-writing-a-chess-engine-c360109371aa) as a possible optimization
- [FEN validation](https://chess.stackexchange.com/a/1483/34173)
