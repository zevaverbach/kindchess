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

# UX
- stickers
- in-person chess 'dating'

# Resources Used
- [generate FEN from board](http://www.netreal.de/Forsyth-Edwards-Notation/index.php)
- [generate board from FEN](http://www.ee.unb.ca/cgi-bin/tervo/fen.pl)
