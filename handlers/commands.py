from telegram import Update
from telegram.ext import ContextTypes

from keyboards.menus import (
    back_to_home_menu,
    main_menu,
    scenarios_menu,
)
from storage import user_states


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """نمایش منوی اصلی از طریق منوی دستورات تلگرام."""
    user = update.effective_user
    user_states.pop(user.id, None)
    await update.effective_message.reply_text(
        "💎 <b>منوی اصلی Clever Minds</b>\n\nیکی از گزینه‌ها را انتخاب کن:",
        reply_markup=main_menu(),
        parse_mode="HTML",
    )


async def create_game_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """باز کردن مستقیم انتخاب سناریو از طریق /create_game."""
    user_states.pop(update.effective_user.id, None)
    await update.effective_message.reply_text(
        "🎭 <b>انتخاب سناریو</b>",
        reply_markup=scenarios_menu(),
        parse_mode="HTML",
    )


async def join_game_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """فعال‌کردن دریافت کد بازی از طریق /join_game."""
    user = update.effective_user
    user_states[user.id] = "waiting_for_game_code"
    await update.effective_message.reply_text(
        "🎮 کد چهاررقمی بازی را ارسال کن.",
        reply_markup=back_to_home_menu(),
    )


async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """نمایش پروفایل از طریق /profile."""
    user = update.effective_user
    user_states.pop(user.id, None)
    await update.effective_message.reply_text(
        text=(
            "👤 <b>پروفایل شما</b>\n\n"
            f"نام: <b>{user.first_name}</b>\n"
            f"شناسه: <code>{user.id}</code>"
        ),
        reply_markup=back_to_home_menu(),
        parse_mode="HTML",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """نمایش راهنما از طریق /help."""
    user_states.pop(update.effective_user.id, None)
    await update.effective_message.reply_text(
        text=(
            "📚 <b>راهنما</b>\n\n"
            "گرداننده بازی می‌سازد و کد را به بازیکنان می‌دهد.\n"
            "بازیکنان درخواست ورود می‌فرستند و گرداننده آن‌ها را تأیید می‌کند."
        ),
        reply_markup=back_to_home_menu(),
        parse_mode="HTML",
    )
