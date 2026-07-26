from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def narrator_lobby_menu(game_code: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "👥 مدیریت بازیکنان",
                    callback_data=f"players:{game_code}",
                )
            ],
            [
                InlineKeyboardButton(
                    "👑 انتقال گردانندگی",
                    callback_data=f"transfer_menu:{game_code}",
                )
            ],
            [
                InlineKeyboardButton(
                    "🔒 بستن ثبت‌نام و قرعه صندلی",
                    callback_data=f"close_registration:{game_code}",
                )
            ],
            [
                InlineKeyboardButton(
                    "🎲 قرعه‌کشی مجدد صندلی‌ها",
                    callback_data=f"randomize_seats:{game_code}",
                )
            ],
            [
                InlineKeyboardButton(
                    "▶️ شروع بازی",
                    callback_data=f"start_game:{game_code}",
                )
            ],
            [
                InlineKeyboardButton(
                    "❌ لغو بازی",
                    callback_data=f"cancel_game:{game_code}",
                )
            ],
        ]
    )


def players_management_menu(game_code: str, players: list[dict]) -> InlineKeyboardMarkup:
    rows = []
    for player in players:
        icon = {
            "pending": "⏳",
            "approved": "✅",
            "rejected": "❌",
        }.get(player["status"], "•")
        seat = f"صندلی {player['seat']} — " if player.get("seat") else ""
        rows.append(
            [
                InlineKeyboardButton(
                    f"{icon} {seat}{player['name']}",
                    callback_data=f"player:{game_code}:{player['user_id']}",
                )
            ]
        )

    rows.append(
        [
            InlineKeyboardButton(
                "⬅️ بازگشت به میز بازی",
                callback_data=f"refresh_game:{game_code}",
            )
        ]
    )
    return InlineKeyboardMarkup(rows)


def player_actions_menu(game_code: str, user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "✅ تأیید",
                    callback_data=f"approve:{game_code}:{user_id}",
                ),
                InlineKeyboardButton(
                    "❌ رد",
                    callback_data=f"reject:{game_code}:{user_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    "👑 انتقال گردانندگی به این شخص",
                    callback_data=f"transfer_confirm:{game_code}:{user_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    "⬅️ بازگشت",
                    callback_data=f"players:{game_code}",
                )
            ],
        ]
    )


def transfer_menu(game_code: str, players: list[dict]) -> InlineKeyboardMarkup:
    rows = []
    for player in players:
        if player["status"] == "approved":
            rows.append(
                [
                    InlineKeyboardButton(
                        f"👤 {player['name']}",
                        callback_data=(
                            f"transfer_confirm:{game_code}:{player['user_id']}"
                        ),
                    )
                ]
            )
    rows.append(
        [
            InlineKeyboardButton(
                "⬅️ بازگشت",
                callback_data=f"refresh_game:{game_code}",
            )
        ]
    )
    return InlineKeyboardMarkup(rows)
