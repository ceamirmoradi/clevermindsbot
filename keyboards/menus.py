from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🎙 ایجاد بازی", callback_data="create_game"),
                InlineKeyboardButton("🎮 ورود با کد", callback_data="join_game"),
            ],
            [
                InlineKeyboardButton("👤 پروفایل من", callback_data="profile"),
                InlineKeyboardButton("📚 راهنمای استفاده", callback_data="help"),
            ],
        ]
    )


def scenarios_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("⚖️ بازپرس ۱۰ نفره", callback_data="scenario:bazpors10")],
            [InlineKeyboardButton("⚖️ بازپرس ۱۲ نفره", callback_data="scenario:bazpors12")],
            [InlineKeyboardButton("⚖️ بازپرس ۱۳ نفره", callback_data="scenario:bazpors13")],
            [InlineKeyboardButton("🤝 مذاکره", callback_data="scenario:mozakere")],
            [InlineKeyboardButton("🦂 عقرب", callback_data="scenario:aghrab")],
            [InlineKeyboardButton("⬅️ بازگشت", callback_data="home")],
        ]
    )


def confirm_scenario_menu(scenario_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "✅ تأیید و ساخت بازی",
                    callback_data=f"confirm_scenario:{scenario_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    "🔄 تغییر سناریو",
                    callback_data="create_game",
                )
            ],
            [InlineKeyboardButton("⬅️ منوی اصلی", callback_data="home")],
        ]
    )


def back_to_home_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ بازگشت به منوی اصلی", callback_data="home")]]
    )


def join_confirmation_menu(game_code: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "✅ ارسال درخواست ورود",
                    callback_data=f"confirm_join:{game_code}",
                )
            ],
            [InlineKeyboardButton("❌ انصراف", callback_data="home")],
        ]
    )
