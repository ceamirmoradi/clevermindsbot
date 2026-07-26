import random
from typing import Any

from scenarios import SCENARIOS
from storage import games


def generate_game_code() -> str:
    for _ in range(200):
        code = str(random.randint(1000, 9999))
        if code not in games:
            return code
    raise RuntimeError("امکان تولید کد یکتا وجود ندارد.")


def get_player(game: dict[str, Any], user_id: int) -> dict[str, Any] | None:
    for player in game["players"]:
        if player["user_id"] == user_id:
            return player
    return None


def approved_players(game: dict[str, Any]) -> list[dict[str, Any]]:
    return [p for p in game["players"] if p["status"] == "approved"]


def pending_players(game: dict[str, Any]) -> list[dict[str, Any]]:
    return [p for p in game["players"] if p["status"] == "pending"]


def next_free_seat(game: dict[str, Any]) -> int | None:
    used = {
        p["seat"]
        for p in game["players"]
        if p["status"] == "approved" and p.get("seat")
    }
    for seat in range(1, game["max_players"] + 1):
        if seat not in used:
            return seat
    return None


def create_game(
    *,
    code: str,
    scenario_id: str,
    narrator_id: int,
    narrator_name: str,
    narrator_chat_id: int,
    lobby_message_id: int,
) -> dict[str, Any]:
    scenario = SCENARIOS[scenario_id]
    game = {
        "code": code,
        "scenario_id": scenario_id,
        "narrator_id": narrator_id,
        "narrator_name": narrator_name,
        "previous_narrator_id": None,
        "players": [],
        "max_players": scenario["player_count"],
        "registration_open": True,
        "status": "waiting",
        "narrator_chat_id": narrator_chat_id,
        "lobby_message_id": lobby_message_id,
        "history": [],
    }
    games[code] = game
    return game


def add_pending_player(
    game: dict[str, Any],
    *,
    user_id: int,
    name: str,
    username: str | None,
) -> dict[str, Any]:
    existing = get_player(game, user_id)
    if existing:
        return existing

    player = {
        "user_id": user_id,
        "name": name,
        "username": username,
        "seat": None,
        "status": "pending",
        "role": None,
        "alive": True,
    }
    game["players"].append(player)
    game["history"].append(f"{name} درخواست ورود داد.")
    return player


def approve_player(game: dict[str, Any], user_id: int) -> dict[str, Any]:
    player = get_player(game, user_id)
    if not player:
        raise ValueError("بازیکن پیدا نشد.")

    if player["status"] != "approved":
        seat = next_free_seat(game)
        if seat is None:
            raise ValueError("همه صندلی‌ها پر هستند.")
        player["status"] = "approved"
        player["seat"] = seat
        game["history"].append(
            f"{player['name']} تأیید شد و روی صندلی {seat} قرار گرفت."
        )
    return player


def reject_player(game: dict[str, Any], user_id: int) -> dict[str, Any]:
    player = get_player(game, user_id)
    if not player:
        raise ValueError("بازیکن پیدا نشد.")

    old_seat = player.get("seat")
    player["status"] = "rejected"
    player["seat"] = None
    game["history"].append(
        f"{player['name']} رد شد"
        + (f" و صندلی {old_seat} آزاد شد." if old_seat else ".")
    )
    return player


def transfer_narrator(
    game: dict[str, Any],
    *,
    new_narrator_id: int,
    new_narrator_name: str,
) -> None:
    old_name = game["narrator_name"]
    game["previous_narrator_id"] = game["narrator_id"]
    game["narrator_id"] = new_narrator_id
    game["narrator_name"] = new_narrator_name
    game["history"].append(
        f"گردانندگی از {old_name} به {new_narrator_name} منتقل شد."
    )
