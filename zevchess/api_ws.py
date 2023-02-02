import asyncio
import json
import typing

import websockets

from zevchess import queries as q


class ConnectionStore(typing.NamedTuple):
    players: set[websockets.ServerConnection] = set() # type: ignore
    watchers: set[websockets.ServerConnection] = set() # type: ignore

CONNECTIONS = {}


class InvalidUid(Exception):
    pass


async def join(ws, uid: str):
    if uid in CONNECTIONS:
        store = CONNECTIONS[uid]
        if len(store.players) == 2:
            store.watchers.add(ws)
            print(f"watcher #{len(store.watchers)} has joined")
            await ws.send(json.dumps({"type": "success", "message": f"you're watching game {uid}, you're joined by {len(store.watchers) - 1} others"}))
        else:
            store.players.add(ws)
            print("second player has joined the game")
            await ws.send(json.dumps({"type": "success", "message": "you are player two, you're playing the black pieces"}))
            try:
                async for message in ws:
                    print(f"second player sent '{message}'")
            finally:
                store.players.remove(ws)
    else:
        if not q.uid_exists_and_is_an_active_game(uid):
            raise InvalidUid
        CONNECTIONS[uid] = ConnectionStore()
        store = CONNECTIONS[uid]
        store.players.add(ws)
        print("first player has joined the game")
        await ws.send(json.dumps({"type": "success", "message": "you are player one, you're playing the white pieces"}))
        try:
            async for message in ws:
                print(f"first player sent '{message}'")
        finally:
            store.players.remove(ws)


async def error(ws, msg: str):
    await ws.send(json.dumps({"type": "error", "message": msg}))

async def handler(ws):
    # TODO: broadcast moves to everyone
    # TODO: end game when a player closes connection
    #           ws.wait_closed()
    async for message in ws:
        event = json.loads(message)
        print(event)
        match event['type']:
            case "join":
                try:
                    await join(ws, event["uid"])
                except InvalidUid:
                    await error(ws, "game not found")
            case "move":
                await move(ws, event) 
            case "resign":
                await resign(ws, event) 
            case "draw":
                await draw(ws, event) 


async def move(ws, uid: str):
    # TODO: return all possible moves
    raise NotImplementedError


async def resign(ws, uid: str):
    raise NotImplementedError


async def draw(ws, uid: str):
    raise NotImplementedError


async def main():
    async with websockets.serve(handler, "", 8001): # type: ignore
        await asyncio.Future() # run forever

if __name__ == "__main__":
    asyncio.run(main())
