import asyncio
import dataclasses as dc
import json
import typing

from websockets.legacy.protocol import (
    broadcast as ws_broadcast,
    WebSocketCommonProtocol as Ws,
)
from websockets.legacy.server import serve as ws_serve

from zevchess import commands as c
from zevchess import print_board
from zevchess import queries as q
from zevchess import ztypes as t


@dc.dataclass
class ConnectionStore:
    uid: str
    white: Ws | None = None
    black: Ws | None = None
    watchers: set[Ws] | None = None


CONNECTIONS = {}
CONNECTION_WS_STORE_DICT: dict[
    str, tuple[ConnectionStore, typing.Literal["black", "white", "watchers"]]
] = {}


class InvalidUid(Exception):
    pass


class InvalidArguments(Exception):
    pass


class NoSuchConnection(Exception):
    pass


class InvalidMoveEvent(Exception):
    pass


async def join(ws, uid: str):
    if uid in CONNECTIONS:
        st = CONNECTIONS[uid]
        if st.white and st.black and ws not in (st.white, st.black):
            if st.watchers is None:
                st.watchers = {ws}
            else:
                st.watchers.add(ws)
            print(f"{st.watchers=}")
            CONNECTION_WS_STORE_DICT[ws] = (st, "watchers")
            print(f"watcher #{len(st.watchers)} has joined")
            return await ws.send(
                json.dumps(
                    {
                        "type": "success",
                        "message": f"you're watching game {uid}, you're joined"
                        f" by {len(st.watchers) - 1} others",
                        "game_state": dc.asdict(q.get_game_state(uid)),
                    }
                )
            )
        st.black = ws
        print("second player has joined the game")
        CONNECTION_WS_STORE_DICT[ws] = (st, "black")
        await ws.send(
            json.dumps(
                {
                    "type": "success",
                    "message": "you are player two, you're playing the black pieces",
                }
            )
        )
        return await st.white.send(
            json.dumps(
                {"type": "message", "message": "okay, let's start! it's your turn."}
            )
        )
    if not q.uid_exists_and_is_an_active_game(uid):
        raise InvalidUid
    CONNECTIONS[uid] = ConnectionStore(uid)
    st = CONNECTIONS[uid]
    st.white = ws
    print("first player has joined the game")
    CONNECTION_WS_STORE_DICT[ws] = (st, "white")
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


async def remove_connection(ws, because_ws_disconnected=True):
    try:
        store, attribute = CONNECTION_WS_STORE_DICT[ws]
    except KeyError as e:
        raise NoSuchConnection(
            f"could not find connection {ws}, so didn't remove it from {CONNECTIONS=}"
        ) from e

    if attribute == "watchers":
        if store.watchers is not None and len(store.watchers) > 0:
            store.watchers.remove(ws)
            print(f"{store.watchers=}")
            if len(store.watchers) > 0:
                ws_broadcast(
                    store.watchers,
                    json.dumps(
                        {
                            "type": "message",
                            "message": f"someone has left chat, there are {len(store.watchers)} left.",
                        }
                    ),
                )
        del CONNECTION_WS_STORE_DICT[ws]
    elif because_ws_disconnected:
        side = attribute
        await game_over(ws=ws, store=store, side=side, reason="abandoned")


async def game_over(
    ws,
    store: ConnectionStore,
    reason: typing.Literal["abandoned", "checkmate", "stalemate", "resigned", "draw"],
    side: typing.Literal["white", "black"],
    the_move: t.Move | None = None,
) -> None:
    winner = None
    match reason:
        case "checkmate":
            msg = f"checkmate! {side} wins"
        case "stalemate":
            msg = "stalemate!"
        case "abandoned":
            other_side = "white" if side == "black" else "white"
            winner = other_side
            msg = f"{side} abandoned the game, so {winner} wins!"
        case "resigned":
            other_side = "white" if side == "black" else "white"
            winner = other_side
            msg = f"{side} has resigned!"
        case "draw":
            msg = "players have agreed to a draw"
        case _:
            raise InvalidArguments

    uid = store.uid
    state = q.get_game_state(store.uid)
    recipients = get_all_participants(store)
    if reason not in ("abandoned", "resigned", "draw"):
        if the_move is None:
            raise InvalidArguments
        non_winner_participants = get_all_participants(store, but=getattr(store, side))
        ws_broadcast(
            non_winner_participants,
            json.dumps(
                {"type": "move", "move": the_move.to_json(), "state": dc.asdict(state)}
            ),
        )
    ws_broadcast(recipients, json.dumps({"type": "game_over", "message": msg}))

    if reason == "abandoned":
        # otherwise, the `checkmate` or `stalemate`
        # field was already set in the core logic
        state.abandoned = 1
        state.winner = 0 if winner == "white" else 1
    elif reason == "resigned":
        state.resigned = 1
        state.winner = 0 if winner == "white" else 1
    print(f"removing game {uid} from cache")
    c.remove_game_from_cache(uid)
    try:
        c.save_game_to_db(uid, state)
    except q.NoSuchGame:
        # the game ended before any moves
        pass
    for p in recipients:
        await p.close()
    if uid in CONNECTIONS:
        del CONNECTIONS[uid]
    await remove_connection(ws, because_ws_disconnected=False)


async def handler(ws):
    async for message in ws:
        try:
            event = json.loads(message)
        except json.decoder.JSONDecodeError:
            print(message)
            await error(ws, "invalid event")
            continue
        print(event)
        if "uid" not in event or "type" not in event:
            print(message)
            await error(ws, "invalid event")
            continue
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
                await resign(ws, uid)
            case "draw":
                if "draw" not in event:
                    await error(ws, "invalid event")
                    continue
                await draw(ws, uid, event["draw"])
            case _:
                print(event)
                await error(ws, "invalid event")
                continue

    else:
        print(f"ws {ws} has disconnected")
        try:
            await remove_connection(ws)
        except NoSuchConnection:
            pass


def get_all_participants(store: ConnectionStore, but: Ws | None = None) -> set[Ws]:
    ps = store.watchers.copy() or set()
    if store.white is not None:
        ps.add(store.white)
    if store.black is not None:
        ps.add(store.black)
    if but is None:
        return ps
    return {p for p in ps if p != but}


async def move(ws, event: dict) -> None:
    uid = event.pop("uid")

    ##############
    # VALIDATION #
    ##############

    try:
        store = CONNECTIONS[uid]
    except KeyError:
        return await error(ws, "no such game!")

    if store.watchers and ws in store.watchers:
        return await error(ws, "you're not a player, can't send moves!")
    if CONNECTION_WS_STORE_DICT[ws][0].uid != uid:
        return await error(ws, "no such game!")

    state = q.get_game_state(uid)

    if (state.turn and ws == store.white) or (state.turn == 0 and ws == store.black):
        return await error(ws, "not your turn!")

    if store.white is None or store.black is None:
        return await error(ws, "we don't have two players, can't make a move!")

    try:
        validate_move_event(event)
    except InvalidMoveEvent as e:
        return await error(ws, str(e))

    if (state.turn and event["piece"].isupper()) or (
        state.turn == 0 and event["piece"].islower()
    ):
        return await error(ws, "that's not your piece!")

    ############
    # THE MOVE #
    ############

    the_move = t.Move(**event)
    try:
        new_state = c.make_move_and_persist(uid=uid, move=the_move, state=state)
    except c.InvalidMove as e:
        print(f"{state=}")
        print(str(e))
        await error(ws, "invalid move")
    except c.NotYourTurn:
        print("someone tried to make a move when it wasn't their turn")
        await error(ws, "not your turn!")
    except c.InvalidState:
        await error(ws, "haven't chosen promotion piece")
    except c.Stalemate as e:
        side = "black" if str(e) == "0" else "white"
        await game_over(
            ws, store=store, reason="stalemate", side=side, the_move=the_move
        )
    except c.Checkmate as e:
        winner = "black" if str(e) == "0" else "white"
        await game_over(
            ws=ws, store=store, side=winner, reason="checkmate", the_move=the_move
        )
    else:
        recipients = get_all_participants(store, but=ws)
        print_board.print_board_from_FEN(new_state.FEN)
        ws_broadcast(
            recipients,
            json.dumps(
                {
                    "type": "move",
                    **the_move.to_json(),
                    "side": "black" if new_state.turn else "white",
                    "state": dc.asdict(new_state),
                }
            ),
        )
        await ws.send(
            json.dumps(
                {
                    "type": "success",
                    "message": "move acknowledged",
                    "move": the_move.to_json(),
                }
            )
        )
        await its_your_move(uid, new_state)


def validate_move_event(event: dict) -> None:
    if not all(field in event for field in ("piece", "src", "dest")):
        raise InvalidMoveEvent(
            "missing fields! must include at least 'src', 'dest', and 'piece'"
        )


async def its_your_move(uid: str, state: t.GameState) -> None:
    all_possible_moves = q.get_all_legal_moves(state)
    turn = state.turn
    store = CONNECTIONS[uid]
    ws = store.black if turn else store.white
    await ws.send(
        json.dumps(
            {
                "type": "possible_moves",
                "possible_moves": [m.to_json() for m in all_possible_moves],
                "message": "it's your turn!",
            }
        )
    )


async def resign(ws, uid: str) -> None:
    store = CONNECTIONS[uid]
    if store.white is None or store.black is None:
        return await error(ws, "we don't have two players, can't resign!")
    requester = "white" if ws == store.white else "black"
    return await game_over(ws, reason="resigned", store=store, side=requester)


async def offer_draw(ws, uid) -> None:
    store = CONNECTIONS[uid]
    if store.white is None or store.black is None:
        return await error(ws, "we don't have two players, can't offer a draw!")
    requester = "white" if ws == store.white else "black"
    side = 0 if ws == store.white else 1
    try:
        c.offer_draw(uid, side)
    except c.InvalidArguments as e:
        await ws.send(str(e))
    else:
        ws_broadcast(get_all_participants(store), f"{requester} offers a draw")


async def withdraw_draw(ws, uid) -> None:
    store = CONNECTIONS[uid]
    requester = "white" if ws == store.white else "black"
    side = 0 if ws == store.white else 1
    try:
        c.withdraw_draw(uid, side)
    except c.InvalidArguments as e:
        await ws.send(str(e))
    else:
        ws_broadcast(
            get_all_participants(store), f"{requester} has withdrawn their draw offer"
        )


async def reject_draw(ws, uid) -> None:
    store = CONNECTIONS[uid]
    requester = "white" if ws == store.white else "black"
    other = "white" if requester == "black" else "black"
    side = 0 if ws == store.white else 1
    try:
        c.reject_draw(uid, side)
    except c.InvalidArguments as e:
        await ws.send(str(e))
    else:
        ws_broadcast(
            get_all_participants(store),
            f"{requester} has rejected {other}'s draw offer",
        )


async def accept_draw(ws, uid: str) -> None:
    store = CONNECTIONS[uid]
    requester = "white" if ws == store.white else "black"
    side = 0 if ws == store.white else 1
    try:
        c.accept_draw(uid, side)
    except c.InvalidArguments as e:
        await ws.send(str(e))
    else:
        return await game_over(ws, store=store, reason="draw", side=requester)


async def draw(
    ws, uid, draw_action: typing.Literal["offer", "accept", "reject", "withdraw"]
) -> None:
    match draw_action:
        case "offer":
            return await offer_draw(ws, uid)
        case "accept":
            return await accept_draw(ws, uid)
        case "reject":
            return await reject_draw(ws, uid)
        case "withdraw":
            return await withdraw_draw(ws, uid)


async def main():
    async with ws_serve(handler, "", 8001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
