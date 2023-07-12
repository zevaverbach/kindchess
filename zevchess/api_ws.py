import asyncio
import dataclasses as dc
import datetime as dt
import http
import json
import os
import signal
import typing

from dotenv import load_dotenv
import websockets as w
from websockets.legacy.protocol import (
    WebSocketCommonProtocol as Ws,
    broadcast as ws_broadcast,
)

from zevchess import commands as c
from zevchess import queries as q
from zevchess import ztypes as t


VALID_ORIGINS = ("http://localhost:8000", 'http://127.0.0.1:5000')

load_dotenv()
if os.getenv("KINDCHESS_ENVIRONMENT") == "prod":
    VALID_ORIGINS = ("https://zevchess-ws.onrender.com",
                     "https://kindchess.com")

@dc.dataclass
class ConnectionStore:
    uid: str
    white: Ws | None = None
    black: Ws | None = None
    watchers: set[Ws] | None = None

CONNECTIONS: dict[str, ConnectionStore] = {}
CONNECTION_WS_STORE_DICT: dict[
    Ws, tuple[ConnectionStore, typing.Literal["black", "white", "watchers"]]
] = {}


class NoOpponent(Exception):
    pass


class InvalidUid(Exception):
    pass


class InvalidArguments(Exception):
    pass


class InvalidMoveEvent(Exception):
    pass


async def handler(ws):
    uid = None
    store = None
    try:
        async for message in ws:
            try:
                event = json.loads(message)
            except json.decoder.JSONDecodeError:
                print(message, "invalid event")
                await error(ws, "invalid event")
                continue
            if "uid" not in event or "type" not in event:
                print(message, "invalid event")
                await error(ws, "invalid event")
                continue
            uid = event["uid"]
            match event["type"]:
                case "join":
                    try:
                        await join(ws, uid)
                    except InvalidUid:
                        await error(ws, "game not found")
                    except (
                        w.exceptions.ConnectionClosedOK, # type: ignore
                        w.exceptions.ConnectionClosedError, # type: ignore
                    ):
                        store = CONNECTIONS[uid]
                        await game_over(store, "abandoned", which_side(ws, store))
                case "rejoin":
                    try:
                        await rejoin(ws, uid, event['side'], event['disconnected_timestamp'])
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
                case "pawn_promote":
                    await pawn_promotion_complete(
                        ws=ws,
                        uid=uid,
                        choice=event["choice"],
                        move_dict=json.loads(event["move"]),
                    )
                case _:
                    print(event, "invalid event")
                    await error(ws, "invalid event")
                    continue
        # else:
        #     print(f"ws {ws} has disconnected at {dt.datetime.now().timestamp()}")
        #     return await remove_connection(ws)
    

    except w.exceptions.ConnectionClosedOK: # type: ignore
        print("connection closed ok")
        return await remove_connection(ws)
    except w.exceptions.ConnectionClosedError as e: # type: ignore
        print("connection closed error", str(e))
        return await remove_connection(ws)



async def remove_connection(ws):
    if ws not in CONNECTION_WS_STORE_DICT:
        print(f"{ws} not in CONNECTION_WS_STORE_DICT")
        return

    store, attribute = CONNECTION_WS_STORE_DICT[ws]

    if attribute == "watchers":
        if store.watchers is not None and len(store.watchers) > 0:
            store.watchers.remove(ws)
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
    else:
        setattr(store, attribute, None)
        message = json.dumps(
                {"type": "disconnect", "disconnected_timestamp": dt.datetime.now().timestamp()}
            )
        print(f"sending message '{message}'")
        ws_broadcast(
            get_all_participants(store), 
            message,
        )
    del CONNECTION_WS_STORE_DICT[ws]



async def error(ws, msg: str):
    await ws.send(json.dumps({"type": "error", "message": msg}))


async def rejoin(ws, uid, side, disconnected_timestamp):
    if uid not in CONNECTIONS:
        if not q.uid_exists_and_is_an_active_game(uid):
            raise InvalidUid
    try:
        st = CONNECTIONS[uid]
    except KeyError:
        return await error(ws, "invalid UID")
    
    if getattr(st, side) is not None:
        print(f"{st=}")
        return await error(ws, "invalid UID")
    if getattr(st, other_color(side)) is None:
        return await game_over(st, "abandoned", side)
    print(f"{st=}")

    game_state = q.get_game_state(uid)
    all_possible_moves = q.get_all_legal_moves(game_state, json=True)
    game_state_dict = dc.asdict(game_state)
    board = t.Board.from_FEN(game_state.FEN).to_array()

    setattr(st, side, ws)
    CONNECTION_WS_STORE_DICT[ws] = (st, side)
    print(f"{side} has rejoined the game")
    await ws.send(
        json.dumps(
            {
                "type": "rejoin_success",
                "game_state": game_state_dict,
                "board": board,
                "possible_moves": all_possible_moves,
            }
        )
    )
    other_ws = getattr(st, other_color(side))
    await other_ws.send(
        json.dumps(
            {
                "type": "rejoin_success",
                }
            )
        )




async def join(ws, uid: str):
    if uid not in CONNECTIONS:
        if not q.uid_exists_and_is_an_active_game(uid):
            raise InvalidUid
        return await first_joiner(ws, uid)

    st = CONNECTIONS[uid]
    game_state = q.get_game_state(uid)
    all_possible_moves = q.get_all_legal_moves(game_state, json=True)
    game_state_dict = dc.asdict(game_state)
    board = t.Board.from_FEN(game_state.FEN).to_array()

    if st.white and st.black and ws not in (st.white, st.black):
        return await add_watcher(ws, uid, st, game_state_dict, board, all_possible_moves)

    if not st.white:
        return await game_over(st, "abandoned", "black")

    await second_joiner(ws, st, game_state_dict, board, all_possible_moves)

    await st.white.send(
            json.dumps(
                {
                    "type": "join_success",
                    "message": "okay, let's start! it's your turn.",
                    "side": "white",
                    "game_status": "ready",
                    "game_state": game_state_dict,
                    "board": board,
                    "possible_moves": all_possible_moves,
                    }
                )
            )


async def first_joiner(ws, uid):
    CONNECTIONS[uid] = ConnectionStore(uid)
    st = CONNECTIONS[uid]
    st.white = ws
    print("first player has joined the game")
    CONNECTION_WS_STORE_DICT[ws] = (st, "white")
    return await ws.send(
            json.dumps(
                {
                    "type": "join_success",
                    "message": "you are player one, you're playing the white pieces",
                    "game_status": "waiting",
                    }
                )
            )


async def add_watcher(ws, uid, st, game_state_dict, board, all_possible_moves):
    if st.watchers is None:
        st.watchers = {ws}
    else:
        st.watchers.add(ws)
    CONNECTION_WS_STORE_DICT[ws] = (st, "watchers")
    print(f"watcher #{len(st.watchers)} has joined")
    return await ws.send(
            json.dumps(
                {
                    "type": "join_success",
                    "message": f"you're watching game {uid}, you're joined"
                    f" by {len(st.watchers) - 1} others",
                    "game_state": game_state_dict,
                    "game_status": "ready",
                    "board": board,
                    "possible_moves": all_possible_moves,
                    }
                )
            )


async def second_joiner(ws, st, game_state_dict, board, all_possible_moves):
    st.black = ws
    print("second player has joined the game")
    CONNECTION_WS_STORE_DICT[ws] = (st, "black")
    await ws.send(
            json.dumps(
                {
                    "type": "join_success",
                    "message": "you are player two, you're playing the black pieces",
                    "side": "black",
                    "game_status": "ready",
                    "game_state": game_state_dict,
                    "board": board,
                    "possible_moves": all_possible_moves,
                    }
                )
            )


async def game_over(
        store: ConnectionStore,
        reason: typing.Literal["abandoned", "checkmate", "stalemate", "resigned", "draw", "draw_by_three_repetitions"],
        side: typing.Literal["white", "black"],
        the_move: t.Move | None = None,
        ) -> None:
    winner = None
    match reason:
        case "checkmate":
            winner = side
            msg = f"checkmate! {winner} wins"
        case "stalemate":
            msg = "stalemate!"
        case "abandoned":
            winner = other_color(side)
            msg = f"{side} abandoned the game, so {winner} wins!"
        case "resigned":
            winner = other_color(side)
            msg = f"{side} has resigned!"
        case "draw":
            msg = "players have agreed to a draw"
        case "draw_by_three_repetitions":
            msg = "it's a draw by threefold repetition"
        case _:
            raise InvalidArguments

    uid = store.uid
    state = None
    state_dict = None
    try:
        state = q.get_game_state(store.uid)
    except q.NoSuchGame:
        # the game ended before any moves
        print(f"no game found for uid {store.uid}")
        pass
    else:
        state_dict = dc.asdict(state)
    recipients = get_all_participants(store)
    if reason in ("checkmate", "stalemate"):
        if the_move is None:
            raise InvalidArguments
        non_winner_participants = get_all_participants(
                store, but=(getattr(store, side),))
        payload = {"type": "move", "move": the_move.to_json()}
        if state:
            payload["game_state"] = state_dict
            ws_broadcast(non_winner_participants, json.dumps(payload))
    ws_broadcast(
            recipients,
            json.dumps(
                {
                    "type": "game_over",
                    "message": msg,
                    "winner": winner,
                    "game_state": state_dict,
                    "reason": reason,
                    }
                ),
            )

    if state is not None and reason == "abandoned":
        # otherwise, the `checkmate` or `stalemate`
        # field was already set in the core logic
        state.abandoned = 1
        state.winner = 0 if winner == "white" else 1
    elif state is not None and reason == "resigned":
        state.resigned = 1
        state.winner = 0 if winner == "white" else 1
    c.remove_game_from_cache(uid)
    if state is not None:
        try:
            c.save_game_to_db(uid, state)
        except q.NoSuchGame:
            # the game ended before any moves
            pass
    if uid in CONNECTIONS:
        store = CONNECTIONS[uid]
        if store.white:
            await store.white.close()
        if store.black:
            await store.black.close()
        if store.watchers:
            for watcher in store.watchers:
                await watcher.close()
        if uid in CONNECTIONS:
            del CONNECTIONS[uid]


def which_side(ws, store):
    return "white" if ws == store.white else "black"


def other_color(color):
    return "black" if color == "white" else "white"


def get_all_participants(store: ConnectionStore, but: tuple[Ws, ...] | None = None) -> set[Ws]:
    if store.watchers is None:
        ps = set()
    else:
        ps = store.watchers.copy()
    if store.white is not None:
        ps.add(store.white)
    if store.black is not None:
        ps.add(store.black)
    if but is None:
        return ps
    return {p for p in ps if p not in but}


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

    ############
    # THE MOVE #
    ############

    the_move = t.Move(**event)
    try:
        new_state = c.make_move_and_persist(
                uid=uid, move=the_move, state=state)
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
                store=store, reason="stalemate", side=side, the_move=the_move
                )
    except c.Checkmate as e:
        winner = "black" if str(e) == "0" else "white"
        await game_over(
                store=store, side=winner, reason="checkmate", the_move=the_move
                )
    else:
        if new_state.need_to_choose_pawn_promotion_piece != "":
            return await pawn_promotion_prompt(
                    ws=ws,
                    need_to_choose=new_state.need_to_choose_pawn_promotion_piece,
                    move=event,
                    )
        if new_state.draw:
            return await draw(ws, uid, "three_repetitions")
        recipients = get_all_participants(store, but=(ws,))
        board = t.Board.from_FEN(new_state.FEN).to_array()
        all_possible_moves = q.get_all_legal_moves(new_state, json=True)
        ws_broadcast(
            recipients,
            json.dumps(
                {
                    "type": "move",
                    "move": the_move.to_json(),
                    "side": "black" if new_state.turn else "white",
                    "game_state": dc.asdict(new_state),
                    "board": board,
                    "possible_moves": all_possible_moves,
                }
            ),
        )
        move_json = the_move.to_json()
        await ws.send(
            json.dumps(
                {
                    "type": "success",
                    "message": "move acknowledged",
                    "game_state": dc.asdict(new_state),
                    "move": move_json,
                }
            )
        )
        await its_your_move(uid, new_state)


def validate_move_event(event: dict) -> None:
    if not all(field in event for field in ("piece", "src", "dest")):
        raise InvalidMoveEvent(
            "missing fields! must include at least 'src', 'dest', and 'piece'"
        )


async def pawn_promotion_prompt(ws, need_to_choose, move) -> None:
    _, dest, _ = need_to_choose.split(" ")
    return await ws.send(
        json.dumps(
            {
                "type": "input_required",
                "message": "choose pawn promotion piece",
                "dest": dest,
                "move": move,
            }
        )
    )


async def draw(
    ws, uid, draw_action: typing.Literal["offer", "accept", "reject", "withdraw", "three_repetitions"]
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
        case "three_repetitions":
            return await three_repetitions_draw(ws, uid)


async def offer_draw(ws, uid) -> None:
    store = CONNECTIONS[uid]
    if store.white is None or store.black is None:
        return await error(ws, "we don't have two players, can't offer a draw!")
    requester = which_side(ws, store)
    try:
        c.offer_draw(uid, 0 if ws == store.white else 1)
    except (c.InvalidArguments, c.NoMoreDraws) as e:
        await error(ws, str(e))
    else:
        ws_broadcast(
            get_watchers(store),
            json.dumps({
                "type": "for_the_watchers",
                "message": f"{requester} offers a draw",
            }))
        other_ws = store.white if ws == store.black else store.black
        await other_ws.send(json.dumps({
            "type": "draw_offer",
            "message": f"{requester} offers a draw",
        }))


async def accept_draw(ws, uid: str) -> None:
    store = CONNECTIONS[uid]
    requester = which_side(ws, store)
    side = 0 if ws == store.white else 1
    try:
        c.accept_draw(uid, side)
    except c.InvalidArguments as e:
        await ws.send(str(e))
    else:
        return await game_over(store=store, reason="draw", side=requester)


async def reject_draw(ws, uid) -> None:
    store = CONNECTIONS[uid]
    requester = which_side(ws, store)
    other = "white" if requester == "black" else "black"
    side = 0 if ws == store.white else 1
    try:
        c.reject_draw(uid, side)
    except c.InvalidArguments as e:
        await error(ws, str(e))
    else:
        ws_broadcast(
            get_watchers(store),
            json.dumps({
                "type": "for_the_watchers",
                "message": f"{requester} has rejected {other}'s draw offer",
            }))
        other_ws = store.white if ws == store.black else store.black
        if other_ws is None:
            raise ValueError("no other player to notify of draw rejection")
        await other_ws.send(json.dumps({
            "type": "draw_reject",
            "message": f"{requester} has rejected {other}'s draw offer",
        }))


async def withdraw_draw(ws, uid) -> None:
    store = CONNECTIONS[uid]
    requester = which_side(ws, store)
    side = 0 if ws == store.white else 1
    try:
        c.withdraw_draw(uid, side)
    except c.InvalidArguments as e:
        await error(ws, str(e))
    else:
        ws_broadcast(
            get_watchers(store),
            json.dumps({
                "type": "for_the_watchers",
                "message": f"{requester} has withdrawn their draw offer"
            }))
        other_ws = store.white if ws == store.black else store.black
        if other_ws is None:
            raise ValueError("no other player to notify of draw withdrawal")
        await other_ws.send(json.dumps({
            "type": "draw_withdraw",
            "message": f"{requester} has withdrawn their draw offer"
        }))


async def three_repetitions_draw(ws, uid):
    store = CONNECTIONS[uid]
    requester = which_side(ws, store)
    return await game_over(store=store, reason="draw_by_three_repetitions", side=requester)


async def its_your_move(uid: str, state: t.GameState) -> None:
    all_possible_moves = q.get_all_legal_moves(state, json=True)
    turn = state.turn
    store = CONNECTIONS[uid]
    ws = store.black if turn else store.white
    if ws is None:
        raise ValueError("no websocket for player whose turn it is")
    await ws.send(
        json.dumps(
            {
                "type": "possible_moves",
                "possible_moves": all_possible_moves,
                "message": "it's your turn!",
            }
        )
    )


async def resign(ws, uid: str) -> None:
    store = CONNECTIONS[uid]
    if store.white is None or store.black is None:
        return await error(ws, "we don't have two players, can't resign!")
    requester = which_side(ws, store)
    return await game_over(reason="resigned", store=store, side=requester)


def get_watchers(store):
    return get_all_participants(store, but=(store.white, store.black))


async def pawn_promotion_complete(ws, uid, choice, move_dict) -> None:
    store = CONNECTIONS[uid]
    state = q.get_game_state(uid)
    the_move = t.Move(**move_dict)
    try:
        new_state = c.choose_promotion_piece(uid, choice, state)
    except c.NoPendingPawnPromotion:
        print(
            "a pawn promotion was attempted to be copmleted, but there isn't a pending one!"
        )
        await error(ws, "there was no pending pawn promotion")
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
            store=store, reason="stalemate", side=side, the_move=the_move
        )
    except c.Checkmate as e:
        winner = "black" if str(e) == "0" else "white"
        await game_over(
            store=store, side=winner, reason="checkmate", the_move=the_move
        )
    else:
        recipients = get_all_participants(store, but=(ws,))
        board = t.Board.from_FEN(new_state.FEN).to_array()
        all_possible_moves = q.get_all_legal_moves(new_state, json=True)
        move = the_move.to_json()
        move["promotion_piece"] = choice.upper(
        ) if store.white == ws else choice
        ws_broadcast(
            recipients,
            json.dumps(
                {
                    "type": "move",
                    "move": move,
                    "side": "black" if new_state.turn else "white",
                    "game_state": dc.asdict(new_state),
                    "board": board,
                    "possible_moves": all_possible_moves,
                }
            ),
        )
        await ws.send(
            json.dumps(
                {
                    "type": "success",
                    "message": "move acknowledged",
                    "game_state": dc.asdict(new_state),
                    "move": the_move.to_json(),
                }
            )
        )
        await its_your_move(uid, new_state)


async def health_check(path, _):
    if path == "/healthz":
        return http.HTTPStatus.OK, [], b"OK\n"


async def main():
    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

    async with w.serve( # type: ignore
        handler,
        host="0.0.0.0",
        port=8081,
        origins=VALID_ORIGINS,
        process_request=health_check,
    ):
        await stop


if __name__ == "__main__":
    asyncio.run(main())
