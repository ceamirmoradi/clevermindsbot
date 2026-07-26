import logging

from telegram import BotCommand
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from config import PORT, TOKEN, WEBHOOK_URL
from handlers.callbacks import button_handler
from handlers.commands import (
    create_game_command,
    help_command,
    join_game_command,
    menu_command,
    profile_command,
)
from handlers.start import start
from handlers.text import text_handler


logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def error_handler(update: object, context) -> None:
    logger.exception(
        "Exception while handling an update:",
        exc_info=context.error,
    )


async def post_init(application: Application) -> None:
    """ثبت منوی دستورات تلگرام تا گزینه‌های Menu واقعاً اجرا شوند."""
    await application.bot.set_my_commands(
        [
            BotCommand("start", "شروع و نمایش صفحه اصلی"),
            BotCommand("menu", "نمایش منوی اصلی"),
            BotCommand("create_game", "ایجاد میز بازی"),
            BotCommand("join_game", "ورود به بازی با کد"),
            BotCommand("profile", "پروفایل من"),
            BotCommand("help", "راهنمای استفاده"),
        ]
    )


def main() -> None:
    if not TOKEN:
        raise RuntimeError("متغیر BOT_TOKEN در Render تنظیم نشده است.")

    application: Application = (
        ApplicationBuilder()
        .token(TOKEN)
        .post_init(post_init)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CommandHandler("create_game", create_game_command))
    application.add_handler(CommandHandler("join_game", join_game_command))
    application.add_handler(CommandHandler("profile", profile_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_handler))
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
