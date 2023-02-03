import asyncio
import dataclasses as dc
import json
import typing

from rich.pretty import pprint
import websockets

from zevchess import commands as c
from zevchess import print_board
from zevchess import queries as q
from zevchess import ztypes as t


@dc.dataclass
class ConnectionStore:
    white: websockets.ServerConnection | None = None # type: ignore
    black: websockets.ServerConnection | None = None # type: ignore
    watchers: set[websockets.ServerConnection] | None = None  # type: ignore


CONNECTIONS = {}


class InvalidUid(Exception):
    pass


async def join(ws, uid: str):
    if uid in CONNECTIONS:
        store = CONNECTIONS[uid]
        if store.white and store.black:
            if store.watchers is None:
                store.watchers = {ws}
            else:
                store.watchers.add(ws)
            print(f"watcher #{len(store.watchers)} has joined")
            await ws.send(
                json.dumps(
                    {
                        "type": "success",
                        "message": f"you're watching game {uid}, you're joined by {len(store.watchers) - 1} others",
                    }
                )
            )
        else:
            store.black = ws
            print("second player has joined the game")
            await ws.send(
                json.dumps(
                    {
                        "type": "success",
                        "message": "you are player two, you're playing the black pieces",
                    }
                )
            )
    else:
        if not q.uid_exists_and_is_an_active_game(uid):
            raise InvalidUid
        CONNECTIONS[uid] = ConnectionStore()
        store = CONNECTIONS[uid]
        store.white = ws
        print("first player has joined the game")
        await ws.send(
            json.dumps(
                {
                    "type": "success",
                    "message": "you are player one, you're playing the white pieces",
                }
            )
        )


async def error(ws, msg: str):
    await ws.send(json.dumps({"type": "error", "message": msg}))


async def handler(ws):
    async for message in ws:
        try:
            event = json.loads(message)
        except json.decoder.JSONDecodeError:
            print(message)
            continue
        print(event)
        uid = event["uid"]
        match event["type"]:
            case "join":
                try:
                    await join(ws, uid)
                except InvalidUid:
                    await error(ws, "game not found")
            case "move":
                del event["type"]
                await move(ws, event)
            case "resign":
                await resign(ws, event)
            case "draw":
                await draw(ws, event)


async def game_over(ws, msg: str, uid: str) -> None:
    store = CONNECTIONS[uid]
    recipients = {store.white, store.black} | (store.watchers or set())
    websockets.broadcast(recipients, json.dumps({"type": "game_over", "message": msg}))  # type: ignore


async def move(ws, event: dict) -> None:
    uid = event.pop("uid")
    store = CONNECTIONS[uid]
    if store.watchers and ws in store.watchers:
        await error(ws, "you're not a player, can't send moves!")
        return
    if store.white is None or store.black is None:
        await error(ws, "we don't have two players, can't make a move!")
        return
    state = q.get_game_state(uid)
    if (state.turn and ws == store.white) or (state.turn == 0 and ws == store.black):
        await error(ws, "not your turn!")
        return
    if (state.turn and event['piece'].isupper()) or (state.turn == 0 and event['piece'].islower()):
        await error(ws, "that's not your piece!")
        return
    try:
        move = t.Move(**event)
        new_state = c.make_move_and_persist(uid=uid, move=move, state=state)
    except c.Stalemate:
        await game_over(ws, uid=uid, msg=f"stalemate!")
    except c.Checkmate as e:
        winner = "black" if str(e) == "0" else "white"
        await game_over(ws, uid=uid, msg=f"checkmate! {winner} wins")
    except c.InvalidMove as e:
        print(f"{state=}")
        print(str(e))
        await error(ws, "invalid move")
    except c.NotYourTurn:
        print("someone tried to make a move when it wasn't their turn")
        await error(ws, "not your turn!")
    except c.InvalidState:
        await error(ws, "haven't chosen promotion piece")
    else:
        response = dc.asdict(new_state)
        pprint(f"{new_state=}")
        print_board.print_board_from_FEN(new_state.FEN)
        recipients = {store.white, store.black} | (store.watchers or set())
        websockets.broadcast(recipients, json.dumps(response))  # type: ignore


async def resign(ws, uid: str):
    raise NotImplementedError


async def draw(ws, uid: str):
    raise NotImplementedError


async def main():
    async with websockets.serve(handler, "", 8001):  # type: ignore
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
