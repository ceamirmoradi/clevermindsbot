from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def current_phase_label(game: dict[str, Any]) -> str:
    phase = game.get("phase", "day")
    number = game.get("day_number", 1) if phase == "day" else game.get("night_number", 1)
    return ("روز" if phase == "day" else "شب") + f" {number}"


def log_event(
    game: dict[str, Any],
    *,
    event_type: str,
    message: str,
    actor_id: int | None = None,
    target_id: int | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    event = {
        "type": event_type,
        "message": message,
        "phase": game.get("phase", "day"),
        "day_number": game.get("day_number", 1),
        "night_number": game.get("night_number", 0),
        "actor_id": actor_id,
        "target_id": target_id,
        "metadata": metadata or {},
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    game.setdefault("events", []).append(event)
    game.setdefault("history", []).append(message)
    return event


def event_log_text(game: dict[str, Any], limit: int = 30) -> str:
    events = game.get("events", [])
    if not events:
        return (
            f"📜 <b>تاریخچه بازی {game['code']}</b>\n\n"
            "هنوز رویدادی ثبت نشده است."
        )

    lines = [f"📜 <b>تاریخچه بازی {game['code']}</b>", ""]
    for event in events[-limit:]:
        phase = event.get("phase", "day")
        number = (
            event.get("day_number", 1)
            if phase == "day"
            else event.get("night_number", 1)
        )
        phase_label = ("روز" if phase == "day" else "شب") + f" {number}"
        lines.append(f"• <b>{phase_label}</b> — {event['message']}")

    if len(events) > limit:
        lines.append(f"\n… {len(events) - limit} رویداد قدیمی‌تر نمایش داده نشده است.")
    return "\n".join(lines)
