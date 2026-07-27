from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def narrator_lobby_menu(game_code: str, game: dict | None = None) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                "👥 مدیریت بازیکنان",
                callback_data=f"players:{game_code}",
            )
        ]
    ]

    if game and game.get("status") == "running":
        if game.get("phase") == "day":
            rows.append([
                InlineKeyboardButton(
                    "🌙 پایان روز و شروع شب",
                    callback_data=f"start_night:{game_code}",
                )
            ])
        else:
            rows.append([
                InlineKeyboardButton(
                    "☀️ پایان شب و شروع روز",
                    callback_data=f"start_day:{game_code}",
                )
            ])
        rows.append([
            InlineKeyboardButton(
                "🎛 ابزارهای بازی",
                callback_data=f"night_tools:{game_code}",
            )
        ])
        rows.append([
            InlineKeyboardButton(
                "📜 تاریخچه بازی",
                callback_data=f"event_log:{game_code}",
            )
        ])
    else:
        rows.extend([
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
        ])

    rows.append([
        InlineKeyboardButton(
            "❌ لغو بازی",
            callback_data=f"cancel_game:{game_code}",
        )
    ])
    return InlineKeyboardMarkup(rows)


def players_management_menu(game_code: str, players: list[dict]) -> InlineKeyboardMarkup:
    rows = []
    for player in players:
        icon = {
            "pending": "⏳",
            "approved": "✅",
            "rejected": "❌",
            "kicked": "🚫",
            "eliminated": "💀",
            "left": "🚪",
        }.get(player["status"], "•")
        seat = f"صندلی {player['seat']} — " if player.get("seat") else ""
        rows.append([
            InlineKeyboardButton(
                f"{icon} {seat}{player['name']}",
                callback_data=f"player:{game_code}:{player['user_id']}",
            )
        ])

    rows.append([
        InlineKeyboardButton(
            "⬅️ بازگشت به میز بازی",
            callback_data=f"refresh_game:{game_code}",
        )
    ])
    return InlineKeyboardMarkup(rows)


def player_actions_menu(
    game_code: str,
    user_id: int,
    *,
    game: dict | None = None,
    player: dict | None = None,
) -> InlineKeyboardMarkup:
    rows = []

    if not game or game.get("status") != "running":
        rows.append([
            InlineKeyboardButton(
                "✅ تأیید",
                callback_data=f"approve:{game_code}:{user_id}",
            ),
            InlineKeyboardButton(
                "❌ رد",
                callback_data=f"reject:{game_code}:{user_id}",
            ),
        ])
        rows.append([
            InlineKeyboardButton(
                "👑 انتقال گردانندگی به این شخص",
                callback_data=f"transfer_confirm:{game_code}:{user_id}",
            )
        ])
    elif (
        game.get("phase") == "day"
        and player
        and player.get("status") == "approved"
        and player.get("alive", True)
    ):
        rows.append([
            InlineKeyboardButton(
                "⚠️ ثبت اخطار",
                callback_data=f"warn_menu:{game_code}:{user_id}",
            )
        ])
        if player.get("speaking_penalty_pending"):
            rows.append([
                InlineKeyboardButton(
                    "🔇 محرومیت صحبت اجرا شد",
                    callback_data=f"penalty_served:{game_code}:{user_id}",
                )
            ])
        if player.get("warnings"):
            rows.append([
                InlineKeyboardButton(
                    "↩️ حذف آخرین اخطار",
                    callback_data=f"warning_undo:{game_code}:{user_id}",
                )
            ])
        rows.append([
            InlineKeyboardButton(
                "🚫 اخراج مستقیم از بازی",
                callback_data=f"kick_menu:{game_code}:{user_id}",
            )
        ])

    rows.append([
        InlineKeyboardButton(
            "⬅️ بازگشت",
            callback_data=f"players:{game_code}",
        )
    ])
    return InlineKeyboardMarkup(rows)


def kick_reason_menu(game_code: str, user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "⚠️ عدم رعایت قوانین",
            callback_data=f"kick:{game_code}:{user_id}:rules",
        )],
        [InlineKeyboardButton(
            "🗯 توهین یا رفتار نامناسب",
            callback_data=f"kick:{game_code}:{user_id}:insult",
        )],
        [InlineKeyboardButton(
            "🚪 ترک یا غیبت مکرر",
            callback_data=f"kick:{game_code}:{user_id}:absence",
        )],
        [InlineKeyboardButton(
            "🎙 تصمیم گرداننده",
            callback_data=f"kick:{game_code}:{user_id}:narrator",
        )],
        [InlineKeyboardButton(
            "⬅️ انصراف",
            callback_data=f"player:{game_code}:{user_id}",
        )],
    ])


def event_log_menu(game_code: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "🔄 به‌روزرسانی",
            callback_data=f"event_log:{game_code}",
        )],
        [InlineKeyboardButton(
            "⬅️ بازگشت به میز بازی",
            callback_data=f"refresh_game:{game_code}",
        )],
    ])


def transfer_menu(game_code: str, players: list[dict]) -> InlineKeyboardMarkup:
    rows = []
    for player in players:
        if player["status"] == "approved":
            rows.append([
                InlineKeyboardButton(
                    f"👤 {player['name']}",
                    callback_data=f"transfer_confirm:{game_code}:{player['user_id']}",
                )
            ])
    rows.append([
        InlineKeyboardButton(
            "⬅️ بازگشت",
            callback_data=f"refresh_game:{game_code}",
        )
    ])
    return InlineKeyboardMarkup(rows)


def warning_reason_menu(game_code: str, user_id: int) -> InlineKeyboardMarkup:
    reasons = [
        ("🔇 صحبت روی صحبت", "overlap"),
        ("📢 بی‌نظمی", "disorder"),
        ("🎭 اشاره یا افشای نقش", "role_hint"),
        ("🚫 جمله ممنوعه", "forbidden_phrase"),
        ("⚖️ بحث با گرداننده", "argue_narrator"),
        ("📡 جهت دادن پس از خروج", "after_exit"),
        ("📵 اختلال در روند بازی", "disruption"),
        ("📝 سایر", "other"),
    ]
    rows = [[InlineKeyboardButton(label, callback_data=f"warn:{game_code}:{user_id}:{code}")] for label, code in reasons]
    rows.append([InlineKeyboardButton("⬅️ انصراف", callback_data=f"player:{game_code}:{user_id}")])
    return InlineKeyboardMarkup(rows)
