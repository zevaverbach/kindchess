import asyncio

import pyperclip

from zevchess.commands import create_game
from zevchess.api_ws import main


uid = create_game()
pyperclip.copy(f'{{"type": "join", "uid": "{uid}"}}')

asyncio.run(main())



