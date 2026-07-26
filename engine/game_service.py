import secrets
from typing import Any

from scenarios import SCENARIOS
from storage import games

_rng = secrets.SystemRandom()


def generate_game_code() -> str:
    for _ in range(200):
        code = str(_rng.randint(1000, 9999))
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


def randomize_seats(game: dict[str, Any]) -> list[dict[str, Any]]:
    """Assign seats randomly and independently from registration order."""
    players = approved_players(game)
    if not players:
        raise ValueError("هیچ بازیکن تأییدشده‌ای وجود ندارد.")
    if game.get("status") == "running":
        raise ValueError("بعد از شروع بازی امکان قرعه‌کشی مجدد صندلی‌ها وجود ندارد.")

    shuffled = players.copy()
    _rng.shuffle(shuffled)
    for seat, player in enumerate(shuffled, start=1):
        player["seat"] = seat

    game["seats_randomized"] = True
    game["history"].append("چیدمان صندلی‌ها به‌صورت تصادفی قرعه‌کشی شد.")
    return sorted(shuffled, key=lambda p: p["seat"])


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
        "seats_randomized": False,
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
        if len(approved_players(game)) >= game["max_players"]:
            raise ValueError("همه ظرفیت‌های میز بازی پر هستند.")
        player["status"] = "approved"
        player["seat"] = None
        game["seats_randomized"] = False
        game["history"].append(
            f"{player['name']} تأیید شد؛ شماره صندلی هنگام قرعه‌کشی تعیین می‌شود."
        )
    return player


def reject_player(game: dict[str, Any], user_id: int) -> dict[str, Any]:
    player = get_player(game, user_id)
    if not player:
        raise ValueError("بازیکن پیدا نشد.")

    old_seat = player.get("seat")
    player["status"] = "rejected"
    player["seat"] = None
    game["seats_randomized"] = False
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
    game["seats_randomized"] = False
    game["history"].append(
        f"گردانندگی از {old_name} به {new_narrator_name} منتقل شد."
    )
