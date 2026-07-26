import os
import logging
from typing import Final

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand,
)
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)


TOKEN: Final = os.getenv("BOT_TOKEN", "")
PORT: Final = int(os.getenv("PORT", "10000"))
WEBHOOK_URL: Final = "https://clevermindsbot.onrender.com"

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)

# اطلاعات موقت بازی‌ها
active_games: dict[int, dict] = {}


def main_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("🎭 ورود به بازی", callback_data="join_game"),
            InlineKeyboardButton("🎙 ساخت بازی", callback_data="create_game"),
        ],
        [
            InlineKeyboardButton("👤 پروفایل من", callback_data="profile"),
            InlineKeyboardButton("🏆 رتبه‌بندی", callback_data="ranking"),
        ],
        [
            InlineKeyboardButton("📚 آموزش بازی", callback_data="help"),
            InlineKeyboardButton("⚙️ تنظیمات", callback_data="settings"),
        ],
        [
            InlineKeyboardButton("💎 درباره Clever Minds", callback_data="about"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def back_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ بازگشت به منوی اصلی", callback_data="home")]]
    )


def narrator_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("👥 لیست بازیکنان", callback_data="players"),
            InlineKeyboardButton("➕ بازکردن ثبت‌نام", callback_data="open_join"),
        ],
        [
            InlineKeyboardButton("🎭 تقسیم نقش‌ها", callback_data="assign_roles"),
            InlineKeyboardButton("▶️ شروع بازی", callback_data="start_game"),
        ],
        [
            InlineKeyboardButton("🌙 شروع شب", callback_data="night"),
            InlineKeyboardButton("☀️ شروع روز", callback_data="day"),
        ],
        [
            InlineKeyboardButton("🗳 رأی‌گیری", callback_data="vote"),
            InlineKeyboardButton("⏱ تایمر صحبت", callback_data="timer"),
        ],
        [
            InlineKeyboardButton("⛔ پایان بازی", callback_data="end_game"),
        ],
        [
            InlineKeyboardButton("⬅️ منوی اصلی", callback_data="home"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    user = update.effective_user

    text = (
        f"سلام <b>{user.first_name}</b> 💎\n\n"
        "به <b>Clever Minds Mafia</b> خوش آمدی.\n\n"
        "اینجا می‌توانی بازی بسازی، وارد بازی شوی، نقش خصوصی بگیری "
        "و تمام مراحل مافیا را با یک محیط ساده و حرفه‌ای مدیریت کنی.\n\n"
        "یکی از گزینه‌های زیر را انتخاب کن:"
    )

    await update.message.reply_text(
        text,
        reply_markup=main_menu(),
        parse_mode="HTML",
    )


async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query
    await query.answer()

    user = query.from_user
    chat_id = query.message.chat_id
    action = query.data

    if action == "home":
        await query.edit_message_text(
            "💎 <b>منوی اصلی Clever Minds</b>\n\nیک گزینه را انتخاب کن:",
            reply_markup=main_menu(),
            parse_mode="HTML",
        )

    elif action == "create_game":
        active_games[chat_id] = {
            "narrator_id": user.id,
            "narrator_name": user.first_name,
            "players": {},
            "status": "waiting",
        }

        await query.edit_message_text(
            "🎙 <b>بازی جدید ساخته شد</b>\n\n"
            f"گرداننده: <b>{user.first_name}</b>\n"
            "وضعیت: در انتظار بازیکنان\n\n"
            "از پنل زیر بازی را مدیریت کن:",
            reply_markup=narrator_menu(),
            parse_mode="HTML",
        )

    elif action == "join_game":
        game = active_games.get(chat_id)

        if not game:
            await query.edit_message_text(
                "❌ در حال حاضر بازی فعالی وجود ندارد.\n\n"
                "ابتدا باید یک نفر بازی جدید بسازد.",
                reply_markup=back_menu(),
            )
            return

        if game["status"] != "waiting":
            await query.edit_message_text(
                "⛔ ثبت‌نام این بازی بسته شده است.",
                reply_markup=back_menu(),
            )
            return

        game["players"][user.id] = {
            "name": user.first_name,
            "username": user.username,
            "alive": True,
            "role": None,
        }

        count = len(game["players"])

        await query.edit_message_text(
            "✅ <b>با موفقیت وارد بازی شدی</b>\n\n"
            f"نام بازیکن: <b>{user.first_name}</b>\n"
            f"تعداد بازیکنان ثبت‌شده: <b>{count}</b>\n\n"
            "پس از شروع بازی، نقش تو به‌صورت خصوصی ارسال می‌شود.",
            reply_markup=back_menu(),
            parse_mode="HTML",
        )

    elif action == "profile":
        await query.edit_message_text(
            "👤 <b>پروفایل شما</b>\n\n"
            f"نام: <b>{user.first_name}</b>\n"
            f"شناسه کاربری: <code>{user.id}</code>\n"
            "تعداد بازی: ۰\n"
            "برد: ۰\n"
            "امتیاز: ۰\n"
            "رتبه: تازه‌وارد 🌱",
            reply_markup=back_menu(),
            parse_mode="HTML",
        )

    elif action == "ranking":
        await query.edit_message_text(
            "🏆 <b>رتبه‌بندی Clever Minds</b>\n\n"
            "این بخش به‌زودی پس از اتصال دیتابیس فعال می‌شود.",
            reply_markup=back_menu(),
            parse_mode="HTML",
        )

    elif action == "help":
        await query.edit_message_text(
            "📚 <b>راهنمای بازی</b>\n\n"
            "۱. گرداننده روی «ساخت بازی» می‌زند.\n"
            "۲. بازیکنان گزینه «ورود به بازی» را انتخاب می‌کنند.\n"
            "۳. گرداننده ثبت‌نام را می‌بندد.\n"
            "۴. نقش‌ها به‌صورت خصوصی ارسال می‌شوند.\n"
            "۵. بات مراحل شب، روز و رأی‌گیری را مدیریت می‌کند.",
            reply_markup=back_menu(),
            parse_mode="HTML",
        )

    elif action == "settings":
        await query.edit_message_text(
            "⚙️ <b>تنظیمات</b>\n\n"
            "🔔 اعلان‌ها: روشن\n"
            "🌐 زبان: فارسی\n"
            "🎨 قالب: Clever Dark\n\n"
            "تنظیمات بیشتر به‌زودی اضافه می‌شود.",
            reply_markup=back_menu(),
            parse_mode="HTML",
        )

    elif action == "about":
        await query.edit_message_text(
            "💎 <b>Clever Minds Mafia</b>\n\n"
            "یک ربات حرفه‌ای برای مدیریت بازی مافیا، "
            "با هدف ایجاد بازی‌های منظم، باکلاس و بدون تنش.",
            reply_markup=back_menu(),
            parse_mode="HTML",
        )

    elif action == "players":
        game = active_games.get(chat_id)

        if not game or not game["players"]:
            text = "👥 هنوز هیچ بازیکنی ثبت‌نام نکرده است."
        else:
            names = [
                f"{index}. {player['name']}"
                for index, player in enumerate(
                    game["players"].values(),
                    start=1,
                )
            ]
            text = "👥 <b>بازیکنان ثبت‌شده</b>\n\n" + "\n".join(names)

        await query.edit_message_text(
            text,
            reply_markup=narrator_menu(),
            parse_mode="HTML",
        )

    elif action == "open_join":
        game = active_games.get(chat_id)

        if game:
            game["status"] = "waiting"

        await query.edit_message_text(
            "✅ ثبت‌نام بازیکنان باز است.\n\n"
            "بازیکنان می‌توانند از منوی اصلی روی «ورود به بازی» بزنند.",
            reply_markup=narrator_menu(),
        )

    elif action == "assign_roles":
        await query.edit_message_text(
            "🎭 بخش تقسیم نقش‌ها در مرحله بعد فعال می‌شود.",
            reply_markup=narrator_menu(),
        )

    elif action == "start_game":
        game = active_games.get(chat_id)

        if game:
            game["status"] = "running"

        await query.edit_message_text(
            "▶️ بازی آغاز شد.\n\nثبت‌نام بازیکنان بسته شد.",
            reply_markup=narrator_menu(),
        )

    elif action == "night":
        await query.edit_message_text(
            "🌙 شب آغاز شد.\n\nهمه بازیکنان چشمان خود را ببندند.",
            reply_markup=narrator_menu(),
        )

    elif action == "day":
        await query.edit_message_text(
            "☀️ روز آغاز شد.\n\nبازیکنان می‌توانند گفتگو را شروع کنند.",
            reply_markup=narrator_menu(),
        )

    elif action == "vote":
        await query.edit_message_text(
            "🗳 بخش رأی‌گیری در مرحله بعد فعال می‌شود.",
            reply_markup=narrator_menu(),
        )

    elif action == "timer":
        await query.edit_message_text(
            "⏱ تایمر حرفه‌ای در مرحله بعد اضافه می‌شود.",
            reply_markup=narrator_menu(),
        )

    elif action == "end_game":
        active_games.pop(chat_id, None)

        await query.edit_message_text(
            "⛔ بازی پایان یافت.\n\nاطلاعات بازی فعلی بسته شد.",
            reply_markup=main_menu(),
        )


async def post_init(application: Application) -> None:
    commands = [
        BotCommand("start", "بازکردن منوی اصلی"),
        BotCommand("play", "ورود به بازی"),
        BotCommand("run", "ساخت بازی"),
        BotCommand("profile", "نمایش پروفایل"),
        BotCommand("help", "راهنمای استفاده"),
    ]
    await application.bot.set_my_commands(commands)


def main() -> None:
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN تنظیم نشده است")

    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .post_init(post_init)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("play", start))
    app.add_handler(CommandHandler("run", start))
    app.add_handler(CommandHandler("profile", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="telegram",
        webhook_url=f"{WEBHOOK_URL}/telegram",
    )


if __name__ == "__main__":
    main()
