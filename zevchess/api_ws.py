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
    uid: str
    white: websockets.ServerConnection | None = None # type: ignore
    black: websockets.ServerConnection | None = None # type: ignore
    watchers: set[websockets.ServerConnection] | None = None  # type: ignore


CONNECTIONS = {}
CONNECTION_WS_STORE_DICT: dict[str, tuple[ConnectionStore, typing.Literal["black", "white", "watchers"]]] = {}


class InvalidUid(Exception):
    pass

class NoSuchConnection(Exception):
    pass


async def join(ws, uid: str):
    if uid in CONNECTIONS:
        store = CONNECTIONS[uid]

        if ws in get_all_participants(store):
            if ws in (store.black, store.white):
                msg = "you're already playing in this game!"
            else:
                msg = "you're already watching this game!"
            return await error(ws, msg)

        if store.white and store.black:
            if store.watchers is None:
                store.watchers = {ws}
            else:
                store.watchers.add(ws)
            CONNECTION_WS_STORE_DICT[ws] = (store, "watchers")
            print(f"watcher #{len(store.watchers)} has joined")
            return await ws.send(
                json.dumps(
                    {
                        "type": "success",
                        "message": f"you're watching game {uid}, you're joined by {len(store.watchers) - 1} others",
                    }
                )
            )
        store.black = ws
        print("second player has joined the game")
        CONNECTION_WS_STORE_DICT[ws] = (store, "black")
        return await ws.send(
            json.dumps(
                {
                    "type": "success",
                    "message": "you are player two, you're playing the black pieces",
                }
            )
        )
    if not q.uid_exists_and_is_an_active_game(uid):
        raise InvalidUid
    CONNECTIONS[uid] = ConnectionStore(uid)
    store = CONNECTIONS[uid]
    store.white = ws
    print("first player has joined the game")
    CONNECTION_WS_STORE_DICT[ws] = (store, "white")
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


async def remove_connection(ws):
    try:
        store, attribute = CONNECTION_WS_STORE_DICT[ws]
    except KeyError:
        raise NoSuchConnection(f"could not find connection {ws}, so didn't remove it from {CONNECTIONS=}")

    if attribute == 'watchers':
        if store.watchers:
            store.watchers.remove(ws)
        del CONNECTION_WS_STORE_DICT[ws]
        websockets.broadcast(store.watchers, json.dumps({"type": "message", "message": f"someone has left chat, there are {len(store.watchers)} left."}))  # type: ignore
    else:
        side = attribute
        await game_over(ws=ws, store=store, side=side, reason="abandoned")



async def game_over(ws, store: ConnectionStore, reason: typing.Literal["abandoned", "checkmate", "stalemate"], side: typing.Literal["white", "black"] | None = None) -> None:
    match reason:
        case "abandoned":
            other_side = "white" if side == "black" else "white"
            msg = f"{side} abandoned the game, so {other_side} wins!"
        case "checkmate":
            msg = f"checkmate! {side} wins"
        case "stalemate":
            msg = f"stalemate!"

    uid = store.uid
    recipients = get_all_participants(store)
    websockets.broadcast(recipients, json.dumps({"type": "game_over", "message": msg}))  # type: ignore

    state = q.get_game_state(store.uid)
    if reason == "abandoned":
        state.abandoned = 1
    # otherwise, the `checkmate` or `stalemate` field was already set in the core logic
    c.save_game_to_db(uid, state)
    c.remove_game_from_cache(uid)
    for p in recipients:
        await p.close()
    if uid in CONNECTIONS:
        del CONNECTIONS[uid]
    del CONNECTION_WS_STORE_DICT[ws]


async def handler(ws):
    async for message in ws:
        try:
            event = json.loads(message)
        except json.decoder.JSONDecodeError:
            print(message)
            return await error(ws, "invalid event")
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
    else:
        print(f"ws {ws} has disconnected")
        await remove_connection(ws)


def get_all_participants(store: ConnectionStore) -> set[websockets.ServerConnection]: # type: ignore
    return {store.white, store.black} | (store.watchers or set())



async def move(ws, event: dict) -> None:
    uid = event.pop("uid")
    store = CONNECTIONS[uid]
    if store.watchers and ws in store.watchers:
        return await error(ws, "you're not a player, can't send moves!")
    # TODO: uncomment
    # if (store.white is not None and store.white != ws) or (store.black is not None and store.black != ws):
    #     return await error(ws, "no such game")
    state = q.get_game_state(uid)

    if (state.turn and ws == store.white) or (state.turn == 0 and ws == store.black):
        return await error(ws, "not your turn!")

    if store.white is None or store.black is None:
        return await error(ws, "we don't have two players, can't make a move!")

    if (state.turn and event['piece'].isupper()) or (state.turn == 0 and event['piece'].islower()):
        return await error(ws, "that's not your piece!")
    try:
        move = t.Move(**event)
        new_state = c.make_move_and_persist(uid=uid, move=move, state=state)
    except c.Stalemate:
        await game_over(ws, store=store, reason="stalemate")
    except c.Checkmate as e:
        winner = "black" if str(e) == "0" else "white"
        await game_over(ws=ws, store=store, side=winner, reason="checkmate")
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
        recipients = get_all_participants(store)
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
