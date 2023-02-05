import asyncio
import time

import pyperclip

from zevchess.api_ws import main
from zevchess.commands import create_game

uid = create_game()




pyperclip.copy(f'{{"type": "move", "uid": "{uid}", "src": "c8", "dest": "e6", "piece": "Q"}}')
time.sleep(.2)
pyperclip.copy(f'{{"type": "move", "uid": "{uid}", "src": "f7", "dest": "g6", "piece": "k"}}')
time.sleep(.2)
pyperclip.copy(f'{{"type": "move", "uid": "{uid}", "src": "b8", "dest": "c8", "piece": "Q", "capture": 1}}')
time.sleep(.2)
pyperclip.copy(f'{{"type": "move", "uid": "{uid}", "src": "d3", "dest": "h7", "piece": "q"}}')
time.sleep(.2)
pyperclip.copy(f'{{"type": "move", "uid": "{uid}", "src": "b7", "dest": "b8", "piece": "Q", "capture": 1}}')
time.sleep(.2)
pyperclip.copy(f'{{"type": "move", "uid": "{uid}", "src": "d8", "dest": "d3", "piece": "q"}}')
time.sleep(.2)
pyperclip.copy(f'{{"type": "move", "uid": "{uid}", "src": "c7", "dest": "b7", "piece": "Q", "capture": 1}}')
time.sleep(.2)
pyperclip.copy(f'{{"type": "move", "uid": "{uid}", "src": "e8", "dest": "f7", "piece": "k"}}')
time.sleep(.2)
pyperclip.copy(f'{{"type": "move", "uid": "{uid}", "src": "c7", "dest": "d7", "piece": "Q", "capture": 1}}')
time.sleep(.2)
pyperclip.copy(f'{{"type": "move", "uid": "{uid}", "src": "f7", "dest": "f6", "piece": "p"}}')
time.sleep(.2)
pyperclip.copy(f'{{"type": "move", "uid": "{uid}", "src": "h2", "dest": "h4", "piece": "P"}}')
time.sleep(.2)
pyperclip.copy(f'{{"type": "move", "uid": "{uid}", "src": "a6", "dest": "h6", "piece": "r"}}')
time.sleep(.2)
pyperclip.copy(f'{{"type": "move", "uid": "{uid}", "src": "a5", "dest": "c7", "piece": "Q", "capture": 1}}')
time.sleep(.2)
pyperclip.copy(f'{{"type": "move", "uid": "{uid}", "src": "h7", "dest": "h5", "piece": "p"}}')
time.sleep(.2)
pyperclip.copy(f'{{"type": "move", "uid": "{uid}", "src": "h5", "dest": "a5", "piece": "Q", "capture": 1}}')
time.sleep(.2)
pyperclip.copy(f'{{"type": "move", "uid": "{uid}", "src": "a8", "dest": "a6", "piece": "r"}}')
time.sleep(.2)
pyperclip.copy(f'{{"type": "move", "uid": "{uid}", "src": "d1", "dest": "h5", "piece": "Q"}}')
time.sleep(.2)
pyperclip.copy(f'{{"type": "move", "uid": "{uid}", "src": "a7", "dest": "a5", "piece": "p"}}')
time.sleep(.2)
pyperclip.copy(f'{{"type": "move", "uid": "{uid}", "src": "e2", "dest": "e3", "piece": "P"}}')
time.sleep(.2)
pyperclip.copy(f'{{"type": "join", "uid": "{uid}"}}')

asyncio.run(main())
