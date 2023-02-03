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


class ConnectionStore(typing.NamedTuple):
    players: set[websockets.ServerConnection] = set()  # type: ignore
    watchers: set[websockets.ServerConnection] = set()  # type: ignore


CONNECTIONS = {}


class InvalidUid(Exception):
    pass


async def join(ws, uid: str):
    if uid in CONNECTIONS:
        store = CONNECTIONS[uid]
        if len(store.players) == 2:
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
            store.players.add(ws)
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
        store.players.add(ws)
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
    # TODO: broadcast moves to everyone
    # TODO: end game when a player closes connection
    #           ws.wait_closed()
    async for message in ws:
        try:
            event = json.loads(message)
        except json.decoder.JSONDecodeError:
            print(message)
            raise
        print(event)
        match event["type"]:
            case "join":
                try:
                    await join(ws, event["uid"])
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
    recipients = CONNECTIONS[uid].watchers | CONNECTIONS[uid].players
    websockets.broadcast(recipients, json.dumps({"type": "game_over", "message": msg}))  # type: ignore


async def move(ws, event: dict) -> None:
    # uid: str,
    # piece: str
    # src: str
    # dest: str
    # capture: int = 0
    # castle: str = ""
    # pawn_promotion: str = "",
    uid = event.pop("uid")
    state = q.get_game_state(uid)
    try:
        # TODO: determine whether this was a bug in the engine or something else:
        # rnb1kbnr/ppp1pppp/8/3p4/3P1q2/5N2/PPPKPPPP/RNBQ1B1R
        # Move(piece='P', src='h2', dest='h3', capture=0, castle=None)
        move = t.Move(**event)
        pprint(move)
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
    except c.InvalidState:
        await error(ws, "haven't chosen promotion piece")
    else:
        response = dc.asdict(new_state)
        pprint(f"{new_state=}")
        print_board.print_board_from_FEN(new_state.FEN)
        recipients = CONNECTIONS[uid].watchers | CONNECTIONS[uid].players
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
