import secrets
from typing import Any

from scenarios import SCENARIOS
from storage import games
from engine.event_service import log_event

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


def active_players(game: dict[str, Any]) -> list[dict[str, Any]]:
    """Players still participating in the running game."""
    return [
        p for p in game["players"]
        if p.get("status") == "approved" and p.get("alive", True)
    ]


def eligible_night_actors(game: dict[str, Any]) -> list[dict[str, Any]]:
    """Only active players may receive or execute night actions."""
    return [
        p for p in active_players(game)
        if p.get("can_act", True)
    ]


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
        "roles_assigned": False,
        "phase": "day",
        "day_number": 1,
        "night_number": 0,
        "events": [],
        "pending_actions": [],
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
        "role_name": None,
        "team": None,
        "alive": True,
        "can_act": True,
        "removed_reason": None,
        "removed_phase": None,
        "kicked_by": None,
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


KICK_REASONS = {
    "rules": "عدم رعایت قوانین",
    "insult": "توهین یا رفتار نامناسب",
    "absence": "ترک یا غیبت مکرر از میز",
    "narrator": "تصمیم گرداننده",
}


def kick_player(
    game: dict[str, Any],
    *,
    user_id: int,
    narrator_id: int,
    reason_code: str,
) -> dict[str, Any]:
    if game.get("status") != "running":
        raise ValueError("اخراج بازیکن فقط بعد از شروع بازی امکان‌پذیر است.")
    if game.get("phase") != "day":
        raise ValueError("اخراج بازیکن فقط در فاز روز انجام می‌شود.")

    player = get_player(game, user_id)
    if not player:
        raise ValueError("بازیکن پیدا نشد.")
    if player.get("status") != "approved" or not player.get("alive", True):
        raise ValueError("این بازیکن دیگر داخل بازی فعال نیست.")

    reason = KICK_REASONS.get(reason_code)
    if not reason:
        raise ValueError("دلیل اخراج معتبر نیست.")

    player["status"] = "kicked"
    player["alive"] = False
    player["can_act"] = False
    player["removed_reason"] = reason
    player["removed_phase"] = "day"
    player["kicked_by"] = narrator_id

    # Any action already queued for this player is invalidated.
    old_actions = game.get("pending_actions", [])
    game["pending_actions"] = [
        action for action in old_actions
        if action.get("actor_id") != user_id
    ]
    cancelled_count = len(old_actions) - len(game["pending_actions"])

    seat = player.get("seat")
    seat_text = f"صندلی {seat} — " if seat else ""
    message = (
        f"🚫 {seat_text}{player['name']} توسط گرداننده اخراج شد. "
        f"دلیل: {reason}"
    )
    if cancelled_count:
        message += f"؛ {cancelled_count} اکشن ثبت‌شده او باطل شد."

    log_event(
        game,
        event_type="player_kicked",
        message=message,
        actor_id=narrator_id,
        target_id=user_id,
        metadata={
            "reason_code": reason_code,
            "reason": reason,
            "cancelled_actions": cancelled_count,
            "role": player.get("role"),
            "team": player.get("team"),
        },
    )
    return player


def start_night(game: dict[str, Any]) -> None:
    if game.get("status") != "running":
        raise ValueError("بازی هنوز شروع نشده است.")
    if game.get("phase") == "night":
        raise ValueError("بازی همین حالا در فاز شب است.")

    game["phase"] = "night"
    game["night_number"] = int(game.get("night_number", 0)) + 1
    game["pending_actions"] = []
    log_event(
        game,
        event_type="phase_changed",
        message=f"🌙 شب {game['night_number']} آغاز شد.",
    )


def start_day(game: dict[str, Any]) -> None:
    if game.get("status") != "running":
        raise ValueError("بازی هنوز شروع نشده است.")
    if game.get("phase") == "day":
        raise ValueError("بازی همین حالا در فاز روز است.")

    game["phase"] = "day"
    game["day_number"] = int(game.get("day_number", 1)) + 1
    game["pending_actions"] = []
    log_event(
        game,
        event_type="phase_changed",
        message=f"☀️ روز {game['day_number']} آغاز شد.",
    )
