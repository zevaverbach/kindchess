import asyncio
import sys
import time

import pyperclip

from zevchess.commands import create_game
from zevchess.api_ws import main


uid = create_game()
pyperclip.copy(f'{{"type": "move", "uid": "{uid}", "src": "c2", "dest": "c3", "piece": "P"}}')
time.sleep(.3)
pyperclip.copy(f'{{"type": "join", "uid": "{uid}"}}')

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--no":
        print('copied new game to clipboard')
        sys.exit()
    asyncio.run(main())



