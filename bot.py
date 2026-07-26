import logging
import os
import random
from typing import Final

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)


TOKEN: Final = os.getenv("BOT_TOKEN", "")
PORT: Final = int(os.getenv("PORT", "10000"))

# حتماً با آدرس واقعی Render خودت یکی باشد
WEBHOOK_URL: Final = "https://clevermindsbot.onrender.com"

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


# -------------------------------------------------------------------
# ذخیره‌سازی موقت
# در مرحله بعد این بخش را به دیتابیس آنلاین وصل می‌کنیم.
# -------------------------------------------------------------------

games: dict[str, dict] = {}

# مشخص می‌کند هر کاربر الان در انتظار وارد کردن چه چیزی است.
user_states: dict[int, str] = {}


# -------------------------------------------------------------------
# اطلاعات سناریوها
# -------------------------------------------------------------------

SCENARIOS = {
    "bazpors": {
        "name": "بازپرس",
        "emoji": "🕵️",
        "player_count": 10,
        "description": "سناریوی ۱۰ نفره بازپرس",
    },
    "mozakere": {
        "name": "مذاکره",
        "emoji": "🤝",
        "player_count": 10,
        "description": "سناریوی ۱۰ نفره مذاکره",
    },
    "aghrab": {
        "name": "عقرب",
        "emoji": "🦂",
        "player_count": 10,
        "description": "سناریوی ۱۰ نفره عقرب",
    },
}


# -------------------------------------------------------------------
# منوها
# -------------------------------------------------------------------

def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🎙 ایجاد بازی",
                    callback_data="create_game",
                ),
                InlineKeyboardButton(
                    "🎮 ورود با کد",
                    callback_data="join_game",
                ),
            ],
            [
                InlineKeyboardButton(
                    "👤 پروفایل من",
                    callback_data="profile",
                ),
                InlineKeyboardButton(
                    "📚 راهنمای استفاده",
                    callback_data="help",
                ),
            ],
        ]
    )


def scenarios_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🕵️ بازپرس",
                    callback_data="scenario:bazpors",
                ),
            ],
            [
                InlineKeyboardButton(
                    "🤝 مذاکره",
                    callback_data="scenario:mozakere",
                ),
            ],
            [
                InlineKeyboardButton(
                    "🦂 عقرب",
                    callback_data="scenario:aghrab",
                ),
            ],
            [
                InlineKeyboardButton(
                    "⬅️ بازگشت",
                    callback_data="home",
                ),
            ],
        ]
    )


def confirm_scenario_menu(scenario_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "✅ تأیید و ساخت بازی",
                    callback_data=f"confirm_scenario:{scenario_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    "🔄 تغییر سناریو",
                    callback_data="create_game",
                ),
            ],
            [
                InlineKeyboardButton(
                    "⬅️ منوی اصلی",
                    callback_data="home",
                ),
            ],
        ]
    )


def narrator_lobby_menu(game_code: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🔄 بروزرسانی بازیکنان",
                    callback_data=f"refresh_game:{game_code}",
                ),
            ],
            [
                InlineKeyboardButton(
                    "👥 لیست بازیکنان",
                    callback_data=f"players:{game_code}",
                ),
                InlineKeyboardButton(
                    "🔒 بستن ثبت‌نام",
                    callback_data=f"close_registration:{game_code}",
                ),
            ],
            [
                InlineKeyboardButton(
                    "▶️ شروع بازی",
                    callback_data=f"start_game:{game_code}",
                ),
            ],
            [
                InlineKeyboardButton(
                    "❌ لغو بازی",
                    callback_data=f"cancel_game:{game_code}",
                ),
            ],
            [
                InlineKeyboardButton(
                    "🏠 منوی اصلی",
                    callback_data="home",
                ),
            ],
        ]
    )


def back_to_home_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "⬅️ بازگشت به منوی اصلی",
                    callback_data="home",
                )
            ]
        ]
    )


def join_confirmation_menu(game_code: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "✅ ثبت‌نام در بازی",
                    callback_data=f"confirm_join:{game_code}",
                ),
            ],
            [
                InlineKeyboardButton(
                    "❌ انصراف",
                    callback_data="home",
                ),
            ],
        ]
    )


# -------------------------------------------------------------------
# ابزارهای بازی
# -------------------------------------------------------------------

def generate_game_code() -> str:
    """
    یک کد چهاررقمی یکتا برای بازی‌های فعال تولید می‌کند.
    """

    for _ in range(100):
        code = str(random.randint(1000, 9999))

        if code not in games:
            return code

    raise RuntimeError("امکان تولید کد یکتا وجود ندارد.")


def get_player_by_user_id(game: dict, user_id: int) -> dict | None:
    for player in game["players"]:
        if player["user_id"] == user_id:
            return player

    return None


def players_text(game: dict) -> str:
    if not game["players"]:
        return "هنوز هیچ بازیکنی ثبت‌نام نکرده است."

    lines = []

    for player in game["players"]:
        username = (
            f"@{player['username']}"
            if player["username"]
            else "بدون نام کاربری"
        )

        lines.append(
            f"{player['seat']}️⃣ "
            f"<b>{player['name']}</b> — {username}"
        )

    return "\n".join(lines)


def narrator_lobby_text(game_code: str) -> str:
    game = games[game_code]
    scenario = SCENARIOS[game["scenario_id"]]

    status_text = (
        "🟢 ثبت‌نام باز است"
        if game["registration_open"]
        else "🔴 ثبت‌نام بسته است"
    )

    return (
        f"🎉 <b>بازی ایجاد شد</b>\n\n"
        f"{scenario['emoji']} سناریو: "
        f"<b>{scenario['name']}</b>\n"
        f"👥 ظرفیت: <b>{game['max_players']} نفر</b>\n"
        f"🎙 گرداننده: <b>{game['narrator_name']}</b>\n\n"
        f"🔑 کد ورود بازی:\n"
        f"<code>{game_code}</code>\n\n"
        f"بازیکنان ثبت‌شده:\n"
        f"<b>{len(game['players'])} / {game['max_players']}</b>\n\n"
        f"{status_text}"
    )


# -------------------------------------------------------------------
# فرمان شروع
# -------------------------------------------------------------------

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    user = update.effective_user

    # هر بار /start زده شود، حالت انتظار قبلی پاک می‌شود.
    user_states.pop(user.id, None)

    text = (
        f"سلام <b>{user.first_name}</b> 💎\n\n"
        f"به <b>Clever Minds Mafia</b> خوش آمدی.\n\n"
        f"برای ساخت بازی یا ورود با کد، یکی از گزینه‌های زیر را انتخاب کن:"
    )

    await update.message.reply_text(
        text=text,
        reply_markup=main_menu(),
        parse_mode="HTML",
    )


# -------------------------------------------------------------------
# مدیریت دکمه‌ها
# -------------------------------------------------------------------

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query
    user = query.from_user
    action = query.data

    await query.answer()

    # ---------------------------------------------------------------
    # منوی اصلی
    # ---------------------------------------------------------------

    if action == "home":
        user_states.pop(user.id, None)

        await query.edit_message_text(
            text=(
                "💎 <b>منوی اصلی Clever Minds</b>\n\n"
                "یکی از گزینه‌های زیر را انتخاب کن:"
            ),
            reply_markup=main_menu(),
            parse_mode="HTML",
        )
        return

    # ---------------------------------------------------------------
    # ساخت بازی
    # ---------------------------------------------------------------

    if action == "create_game":
        await query.edit_message_text(
            text=(
                "🎭 <b>انتخاب سناریو</b>\n\n"
                "سناریوی موردنظر خود را انتخاب کنید:"
            ),
            reply_markup=scenarios_menu(),
            parse_mode="HTML",
        )
        return

    if action.startswith("scenario:"):
        scenario_id = action.split(":", 1)[1]
        scenario = SCENARIOS.get(scenario_id)

        if not scenario:
            await query.edit_message_text(
                text="❌ سناریوی انتخاب‌شده پیدا نشد.",
                reply_markup=back_to_home_menu(),
            )
            return

        await query.edit_message_text(
            text=(
                f"{scenario['emoji']} "
                f"<b>سناریوی {scenario['name']}</b>\n\n"
                f"👥 تعداد بازیکنان: "
                f"<b>{scenario['player_count']} نفر</b>\n\n"
                f"📝 {scenario['description']}\n\n"
                f"آیا این سناریو را برای بازی انتخاب می‌کنید؟"
            ),
            reply_markup=confirm_scenario_menu(scenario_id),
            parse_mode="HTML",
        )
        return

    if action.startswith("confirm_scenario:"):
        scenario_id = action.split(":", 1)[1]
        scenario = SCENARIOS.get(scenario_id)

        if not scenario:
            await query.edit_message_text(
                text="❌ سناریوی انتخاب‌شده معتبر نیست.",
                reply_markup=back_to_home_menu(),
            )
            return

        # جلوگیری از ساخت چند بازی فعال توسط یک گرداننده
        for code, game in games.items():
            if (
                game["narrator_id"] == user.id
                and game["status"] in {"waiting", "running"}
            ):
                await query.edit_message_text(
                    text=(
                        "⚠️ شما همین حالا یک بازی فعال دارید.\n\n"
                        f"کد بازی فعال شما:\n"
                        f"<code>{code}</code>"
                    ),
                    reply_markup=narrator_lobby_menu(code),
                    parse_mode="HTML",
                )
                return

        game_code = generate_game_code()

        games[game_code] = {
            "code": game_code,
            "scenario_id": scenario_id,
            "narrator_id": user.id,
            "narrator_name": user.first_name,
            "players": [],
            "max_players": scenario["player_count"],
            "registration_open": True,
            "status": "waiting",
        }

        await query.edit_message_text(
            text=narrator_lobby_text(game_code),
            reply_markup=narrator_lobby_menu(game_code),
            parse_mode="HTML",
        )
        return

    # ---------------------------------------------------------------
    # ورود بازیکن با کد
    # ---------------------------------------------------------------

    if action == "join_game":
        user_states[user.id] = "waiting_for_game_code"

        await query.edit_message_text(
            text=(
                "🎮 <b>ورود به بازی</b>\n\n"
                "کد چهاررقمی بازی را ارسال کن.\n\n"
                "مثال:\n"
                "<code>4821</code>"
            ),
            reply_markup=back_to_home_menu(),
            parse_mode="HTML",
        )
        return

    if action.startswith("confirm_join:"):
        game_code = action.split(":", 1)[1]
        game = games.get(game_code)

        if not game:
            await query.edit_message_text(
                text="❌ این بازی دیگر فعال نیست.",
                reply_markup=back_to_home_menu(),
            )
            return

        if not game["registration_open"]:
            await query.edit_message_text(
                text="🔒 ثبت‌نام این بازی بسته شده است.",
                reply_markup=back_to_home_menu(),
            )
            return

        if len(game["players"]) >= game["max_players"]:
            await query.edit_message_text(
                text="⛔ ظرفیت این بازی تکمیل شده است.",
                reply_markup=back_to_home_menu(),
            )
            return

        existing_player = get_player_by_user_id(game, user.id)

        if existing_player:
            await query.edit_message_text(
                text=(
                    "⚠️ شما قبلاً در این بازی ثبت‌نام کرده‌اید.\n\n"
                    f"🪑 شماره صندلی شما: "
                    f"<b>{existing_player['seat']}</b>"
                ),
                reply_markup=back_to_home_menu(),
                parse_mode="HTML",
            )
            return

        seat_number = len(game["players"]) + 1

        player = {
            "user_id": user.id,
            "name": user.first_name,
            "username": user.username,
            "seat": seat_number,
            "role": None,
            "alive": True,
        }

        game["players"].append(player)
        user_states.pop(user.id, None)

        scenario = SCENARIOS[game["scenario_id"]]

        await query.edit_message_text(
            text=(
                "✅ <b>ثبت‌نام شما انجام شد</b>\n\n"
                f"{scenario['emoji']} سناریو: "
                f"<b>{scenario['name']}</b>\n"
                f"🔑 کد بازی: <code>{game_code}</code>\n"
                f"🪑 شماره صندلی شما: <b>{seat_number}</b>\n\n"
                f"👥 تعداد بازیکنان:\n"
                f"<b>{len(game['players'])} / "
                f"{game['max_players']}</b>\n\n"
                "منتظر شروع بازی توسط گرداننده بمانید."
            ),
            reply_markup=back_to_home_menu(),
            parse_mode="HTML",
        )

        # ارسال اطلاع خصوصی به گرداننده
        try:
            await context.bot.send_message(
                chat_id=game["narrator_id"],
                text=(
                    "➕ <b>بازیکن جدید ثبت‌نام کرد</b>\n\n"
                    f"🪑 صندلی {seat_number}\n"
                    f"👤 {user.first_name}\n\n"
                    f"👥 تعداد بازیکنان:\n"
                    f"<b>{len(game['players'])} / "
                    f"{game['max_players']}</b>"
                ),
                reply_markup=narrator_lobby_menu(game_code),
                parse_mode="HTML",
            )
        except Exception as error:
            logger.warning(
                "Could not notify narrator: %s",
                error,
            )

        return

    # ---------------------------------------------------------------
    # پنل گرداننده
    # ---------------------------------------------------------------

    if action.startswith("refresh_game:"):
        game_code = action.split(":", 1)[1]
        game = games.get(game_code)

        if not game:
            await query.edit_message_text(
                text="❌ بازی پیدا نشد.",
                reply_markup=back_to_home_menu(),
            )
            return

        if game["narrator_id"] != user.id:
            await query.answer(
                text="فقط گرداننده به این بخش دسترسی دارد.",
                show_alert=True,
            )
            return

        await query.edit_message_text(
            text=narrator_lobby_text(game_code),
            reply_markup=narrator_lobby_menu(game_code),
            parse_mode="HTML",
        )
        return

    if action.startswith("players:"):
        game_code = action.split(":", 1)[1]
        game = games.get(game_code)

        if not game:
            await query.edit_message_text(
                text="❌ بازی پیدا نشد.",
                reply_markup=back_to_home_menu(),
            )
            return

        if game["narrator_id"] != user.id:
            await query.answer(
                text="فقط گرداننده به این بخش دسترسی دارد.",
                show_alert=True,
            )
            return

        await query.edit_message_text(
            text=(
                f"👥 <b>بازیکنان بازی {game_code}</b>\n\n"
                f"{players_text(game)}\n\n"
                f"تعداد: "
                f"<b>{len(game['players'])} / "
                f"{game['max_players']}</b>"
            ),
            reply_markup=narrator_lobby_menu(game_code),
            parse_mode="HTML",
        )
        return

    if action.startswith("close_registration:"):
        game_code = action.split(":", 1)[1]
        game = games.get(game_code)

        if not game:
            await query.edit_message_text(
                text="❌ بازی پیدا نشد.",
                reply_markup=back_to_home_menu(),
            )
            return

        if game["narrator_id"] != user.id:
            await query.answer(
                text="فقط گرداننده می‌تواند ثبت‌نام را ببندد.",
                show_alert=True,
            )
            return

        game["registration_open"] = False

        await query.edit_message_text(
            text=(
                "🔒 <b>ثبت‌نام بسته شد</b>\n\n"
                f"کد بازی: <code>{game_code}</code>\n"
                f"بازیکنان: "
                f"<b>{len(game['players'])} / "
                f"{game['max_players']}</b>"
            ),
            reply_markup=narrator_lobby_menu(game_code),
            parse_mode="HTML",
        )
        return

    if action.startswith("start_game:"):
        game_code = action.split(":", 1)[1]
        game = games.get(game_code)

        if not game:
            await query.edit_message_text(
                text="❌ بازی پیدا نشد.",
                reply_markup=back_to_home_menu(),
            )
            return

        if game["narrator_id"] != user.id:
            await query.answer(
                text="فقط گرداننده می‌تواند بازی را شروع کند.",
                show_alert=True,
            )
            return

        current_players = len(game["players"])

        if current_players != game["max_players"]:
            await query.answer(
                text=(
                    f"برای شروع باید دقیقاً "
                    f"{game['max_players']} بازیکن ثبت‌نام کرده باشند.\n"
                    f"تعداد فعلی: {current_players}"
                ),
                show_alert=True,
            )
            return

        game["registration_open"] = False
        game["status"] = "running"

        await query.edit_message_text(
            text=(
                "▶️ <b>بازی آماده شروع است</b>\n\n"
                f"🔑 کد بازی: <code>{game_code}</code>\n"
                f"👥 تعداد بازیکنان: "
                f"<b>{current_players}</b>\n\n"
                "در مرحله بعد، ترکیب نقش‌های سناریو و "
                "تقسیم خصوصی نقش‌ها را اضافه می‌کنیم."
            ),
            reply_markup=back_to_home_menu(),
            parse_mode="HTML",
        )
        return

    if action.startswith("cancel_game:"):
        game_code = action.split(":", 1)[1]
        game = games.get(game_code)

        if not game:
            await query.edit_message_text(
                text="❌ بازی قبلاً حذف شده است.",
                reply_markup=back_to_home_menu(),
            )
            return

        if game["narrator_id"] != user.id:
            await query.answer(
                text="فقط گرداننده می‌تواند بازی را لغو کند.",
                show_alert=True,
            )
            return

        del games[game_code]

        await query.edit_message_text(
            text="❌ بازی با موفقیت لغو شد.",
            reply_markup=main_menu(),
        )
        return

    # ---------------------------------------------------------------
    # بخش‌های عمومی
    # ---------------------------------------------------------------

    if action == "profile":
        await query.edit_message_text(
            text=(
                "👤 <b>پروفایل شما</b>\n\n"
                f"نام: <b>{user.first_name}</b>\n"
                f"شناسه: <code>{user.id}</code>\n\n"
                "آمار بازی در نسخه بعدی به دیتابیس متصل می‌شود."
            ),
            reply_markup=back_to_home_menu(),
            parse_mode="HTML",
        )
        return

    if action == "help":
        await query.edit_message_text(
            text=(
                "📚 <b>راهنمای Clever Minds</b>\n\n"
                "🎙 <b>گرداننده:</b>\n"
                "۱. ایجاد بازی را انتخاب کند.\n"
                "۲. سناریو را انتخاب کند.\n"
                "۳. کد چهاررقمی را به بازیکنان بدهد.\n"
                "۴. بعد از ثبت‌نام ۱۰ نفر، بازی را شروع کند.\n\n"
                "🎮 <b>بازیکن:</b>\n"
                "۱. ورود با کد را انتخاب کند.\n"
                "۲. کد چهاررقمی را ارسال کند.\n"
                "۳. ثبت‌نام را تأیید کند."
            ),
            reply_markup=back_to_home_menu(),
            parse_mode="HTML",
        )
        return


# -------------------------------------------------------------------
# دریافت کد چهاررقمی از بازیکن
# -------------------------------------------------------------------

async def text_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    user = update.effective_user
    message = update.message
    text = message.text.strip()

    state = user_states.get(user.id)

    if state != "waiting_for_game_code":
        await message.reply_text(
            text=(
                "برای استفاده از بات، ابتدا منوی اصلی را باز کن."
            ),
            reply_markup=main_menu(),
        )
        return

    if not text.isdigit() or len(text) != 4:
        await message.reply_text(
            text=(
                "❌ کد باید دقیقاً چهار رقم باشد.\n\n"
                "مثال:\n"
                "<code>4821</code>"
            ),
            parse_mode="HTML",
        )
        return

    game = games.get(text)

    if not game:
        await message.reply_text(
            text=(
                "❌ بازی فعالی با این کد پیدا نشد.\n\n"
                "کد را بررسی کن و دوباره ارسال کن."
            ),
            parse_mode="HTML",
        )
        return

    if not game["registration_open"]:
        user_states.pop(user.id, None)

        await message.reply_text(
            text="🔒 ثبت‌نام این بازی بسته شده است.",
            reply_markup=back_to_home_menu(),
        )
        return

    if len(game["players"]) >= game["max_players"]:
        user_states.pop(user.id, None)

        await message.reply_text(
            text="⛔ ظرفیت این بازی تکمیل شده است.",
            reply_markup=back_to_home_menu(),
        )
        return

    scenario = SCENARIOS[game["scenario_id"]]

    await message.reply_text(
        text=(
            f"🎮 <b>بازی پیدا شد</b>\n\n"
            f"{scenario['emoji']} سناریو: "
            f"<b>{scenario['name']}</b>\n"
            f"🎙 گرداننده: "
            f"<b>{game['narrator_name']}</b>\n"
            f"👥 بازیکنان: "
            f"<b>{len(game['players'])} / "
            f"{game['max_players']}</b>\n"
            f"🔑 کد: <code>{text}</code>\n\n"
            "آیا می‌خواهی در این بازی ثبت‌نام کنی؟"
        ),
        reply_markup=join_confirmation_menu(text),
        parse_mode="HTML",
    )


# -------------------------------------------------------------------
# خطاها
# -------------------------------------------------------------------

async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    logger.exception(
        "Exception while handling an update:",
        exc_info=context.error,
    )


# -------------------------------------------------------------------
# اجرای برنامه
# -------------------------------------------------------------------

def main() -> None:
    if not TOKEN:
        raise RuntimeError(
            "متغیر BOT_TOKEN در Render تنظیم نشده است."
        )

    application: Application = (
        ApplicationBuilder()
        .token(TOKEN)
        .build()
    )

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CallbackQueryHandler(button_handler)
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            text_handler,
        )
    )

    application.add_error_handler(error_handler)

    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="telegram",
        webhook_url=f"{WEBHOOK_URL}/telegram",
    )


if __name__ == "__main__":
    main()
