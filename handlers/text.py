from telegram import Update
from telegram.ext import ContextTypes

from keyboards.menus import (
    back_to_home_menu,
    join_confirmation_menu,
    main_menu,
)
from scenarios import SCENARIOS
from storage import games, user_states


async def text_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    user = update.effective_user
    message = update.message
    text = message.text.strip()

    if user_states.get(user.id) != "waiting_for_game_code":
        await message.reply_text(
            "برای استفاده از بات، ابتدا منوی اصلی را باز کن.",
            reply_markup=main_menu(),
        )
        return

    if not text.isdigit() or len(text) != 4:
        await message.reply_text(
            "❌ کد باید دقیقاً چهار رقم باشد.\nمثال: <code>4821</code>",
            parse_mode="HTML",
        )
        return

    game = games.get(text)
    if not game:
        await message.reply_text("❌ بازی فعالی با این کد پیدا نشد.")
        return

    if not game["registration_open"]:
        user_states.pop(user.id, None)
        await message.reply_text(
            "🔒 ثبت‌نام این بازی بسته شده است.",
            reply_markup=back_to_home_menu(),
        )
        return

    scenario = SCENARIOS[game["scenario_id"]]
    await message.reply_text(
        text=(
            f"🎮 <b>بازی پیدا شد</b>\n\n"
            f"{scenario['emoji']} سناریو: <b>{scenario['name']}</b>\n"
            f"🎙 گرداننده: <b>{game['narrator_name']}</b>\n"
            f"🔑 کد: <code>{text}</code>\n\n"
            "برای ارسال درخواست ورود، دکمه زیر را بزن."
        ),
        reply_markup=join_confirmation_menu(text),
        parse_mode="HTML",
    )
