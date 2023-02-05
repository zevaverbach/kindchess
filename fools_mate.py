import asyncio
import time

import pyperclip

from zevchess.api_ws import main
from zevchess.commands import create_game

uid = create_game()

pyperclip.copy(f'{{"type": "move", "uid": "{uid}", "src": "d8", "dest": "h4", "piece": "q"}}')
time.sleep(.2)
pyperclip.copy(f'{{"type": "move", "uid": "{uid}", "src": "g2", "dest": "g4", "piece": "P"}}')
time.sleep(.2)
pyperclip.copy(f'{{"type": "move", "uid": "{uid}", "src": "e7", "dest": "e5", "piece": "p"}}')
time.sleep(.2)
pyperclip.copy(f'{{"type": "move", "uid": "{uid}", "src": "f2", "dest": "f3", "piece": "P"}}')
time.sleep(.2)
pyperclip.copy(f'{{"type": "join", "uid": "{uid}"}}')

asyncio.run(main())
