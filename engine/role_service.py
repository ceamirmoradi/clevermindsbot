import secrets
from typing import Any

from scenarios import SCENARIOS
from storage import save_games

_rng = secrets.SystemRandom()


def assign_roles(game: dict[str, Any]) -> list[dict[str, Any]]:
    """Randomly assign the selected scenario's roles to approved players."""
    scenario = SCENARIOS[game["scenario_id"]]
    role_ids = list(scenario.get("role_ids", []))
    roles = scenario.get("roles", {})

    players = [p for p in game["players"] if p["status"] == "approved"]
    if not role_ids or not roles:
        raise ValueError("نقش‌های این سناریو هنوز داخل بات تعریف نشده‌اند.")
    if len(role_ids) != scenario["player_count"]:
        raise ValueError("تعداد نقش‌های سناریو با تعداد بازیکنان برابر نیست.")
    if len(players) != len(role_ids):
        raise ValueError("تعداد بازیکنان تأییدشده با تعداد نقش‌ها برابر نیست.")
    if game.get("roles_assigned"):
        raise ValueError("نقش‌ها قبلاً تقسیم شده‌اند.")

    shuffled_roles = role_ids.copy()
    _rng.shuffle(shuffled_roles)

    # Seat order is used only for a stable narrator list; assignment remains random.
    ordered_players = sorted(players, key=lambda p: p.get("seat") or 999)
    for player, role_id in zip(ordered_players, shuffled_roles):
        role = roles[role_id]
        player["role"] = role_id
        player["team"] = role["team"]
        player["role_name"] = role["name"]

    game["roles_assigned"] = True
    game["history"].append("نقش‌ها به‌صورت تصادفی میان بازیکنان تقسیم شدند.")
    save_games()
    return ordered_players


def role_for_player(game: dict[str, Any], player: dict[str, Any]) -> dict[str, Any]:
    scenario = SCENARIOS[game["scenario_id"]]
    role_id = player.get("role")
    if not role_id:
        raise ValueError("برای این بازیکن هنوز نقشی تعیین نشده است.")
    if role_id == "yakuzad":
        return {"id":"yakuzad","name":"مافیای یاکوزایی‌شده","emoji":"🤝","team":"mafia","team_name":"مافیا","description":"در طول بازی با یاکوزا به تیم مافیا پیوسته است."}
    return scenario["roles"][role_id]


def private_role_message(game: dict[str, Any], player: dict[str, Any]) -> str:
    role = role_for_player(game, player)
    return (
        f"🎭 نقش شما در سناریوی {SCENARIOS[game['scenario_id']]['name']}\n\n"
        f"{role['emoji']} {role['name']}\n"
        f"🏳️ ساید: {role['team_name']}\n"
        f"🪑 صندلی: {player['seat']}\n\n"
        f"{role['description']}\n\n"
        "⚠️ این پیام خصوصی است؛ نقش خود را برای دیگران ارسال نکن."
    )


def narrator_roles_message(game: dict[str, Any]) -> str:
    scenario = SCENARIOS[game["scenario_id"]]
    lines = [
        f"🎭 فهرست محرمانه نقش‌ها — بازی {game['code']}",
        f"{scenario['emoji']} سناریو: {scenario['name']}",
        "",
    ]
    players = sorted(
        [p for p in game["players"] if p["status"] == "approved"],
        key=lambda p: p.get("seat") or 999,
    )
    for player in players:
        role = role_for_player(game, player)
        lines.append(
            f"{player['seat']}. {player['name']} — {role['emoji']} {role['name']} ({role['team_name']})"
        )
    lines.append("\n🔐 این فهرست فقط برای گرداننده است.")
    return "\n".join(lines)
