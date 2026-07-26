from typing import Any

from engine.game_service import approved_players, pending_players
from scenarios import SCENARIOS


def status_label(status: str) -> str:
    return {
        "pending": "⏳ در انتظار",
        "approved": "✅ تأییدشده",
        "rejected": "❌ ردشده",
        "kicked": "🚫 اخراج‌شده توسط گرداننده",
        "eliminated": "💀 خارج‌شده از بازی",
        "left": "🚪 ترک کرده",
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
    roles_status = "🎭 نقش‌ها تقسیم شده‌اند" if game.get("roles_assigned") else "⏳ نقش‌ها هنوز تقسیم نشده‌اند"
    if game.get("status") == "running":
        phase = game.get("phase", "day")
        phase_number = game.get("day_number", 1) if phase == "day" else game.get("night_number", 1)
        phase_status = ("☀️ روز" if phase == "day" else "🌙 شب") + f" {phase_number}"
    else:
        phase_status = "⏳ بازی هنوز شروع نشده است"

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
        f"{seating}\n"
        f"{roles_status}\n"
        f"{phase_status}\n\n"
        f"<b>چیدمان بازیکنان</b>\n"
        + "\n".join(player_lines)
    )


def player_detail_text(player: dict[str, Any]) -> str:
    username = f"@{player['username']}" if player.get("username") else "ندارد"
    seat = player.get("seat") or "در انتظار قرعه‌کشی"
    extra = ""
    if player.get("status") == "kicked":
        extra = (
            f"\nدلیل اخراج: <b>{player.get('removed_reason') or 'ثبت نشده'}</b>"
            f"\nفاز خروج: <b>روز</b>"
        )
    return (
        f"👤 <b>{player['name']}</b>\n\n"
        f"وضعیت: <b>{status_label(player['status'])}</b>\n"
        f"صندلی: <b>{seat}</b>\n"
        f"نام کاربری: {username}"
        f"{extra}"
    )
