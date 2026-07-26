from typing import Any

from engine.game_service import approved_players, pending_players
from scenarios import SCENARIOS


def status_label(status: str) -> str:
    return {
        "pending": "⏳ در انتظار",
        "approved": "✅ تأییدشده",
        "rejected": "❌ ردشده",
    }.get(status, status)


def narrator_lobby_text(game: dict[str, Any]) -> str:
    scenario = SCENARIOS[game["scenario_id"]]
    approved = approved_players(game)
    pending = pending_players(game)

    player_lines = []
    if game.get("seats_randomized"):
        for player in sorted(approved, key=lambda p: p.get("seat") or 999):
            player_lines.append(f"{player['seat']}. <b>{player['name']}</b> ✅")
    else:
        for player in approved:
            player_lines.append(f"• <b>{player['name']}</b> ✅ — صندلی در انتظار قرعه")

    if not player_lines:
        player_lines.append("هنوز بازیکن تأییدشده‌ای وجود ندارد.")

    registration = (
        "🟢 ثبت‌نام باز است"
        if game["registration_open"]
        else "🔴 ثبت‌نام بسته است"
    )
    seating = (
        "🎲 صندلی‌ها قرعه‌کشی شده‌اند"
        if game.get("seats_randomized")
        else "⏳ صندلی‌ها هنوز قرعه‌کشی نشده‌اند"
    )

    return (
        f"🎭 <b>میز بازی {game['code']}</b>\n\n"
        f"{scenario['emoji']} سناریو: <b>{scenario['name']}</b>\n"
        f"🎙 گرداننده: <b>{game['narrator_name']}</b>\n"
        f"🔑 کد ورود: <code>{game['code']}</code>\n\n"
        f"👥 تأییدشده: <b>{len(approved)} / {game['max_players']}</b>\n"
        f"⏳ در انتظار تأیید: <b>{len(pending)}</b>\n"
        f"{registration}\n"
        f"{seating}\n\n"
        f"<b>چیدمان بازیکنان</b>\n"
        + "\n".join(player_lines)
    )


def player_detail_text(player: dict[str, Any]) -> str:
    username = f"@{player['username']}" if player.get("username") else "ندارد"
    seat = player.get("seat") or "در انتظار قرعه‌کشی"
    return (
        f"👤 <b>{player['name']}</b>\n\n"
        f"وضعیت: <b>{status_label(player['status'])}</b>\n"
        f"صندلی: <b>{seat}</b>\n"
        f"نام کاربری: {username}"
    )
