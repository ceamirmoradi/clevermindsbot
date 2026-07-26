import logging

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


def main() -> None:
    if not TOKEN:
        raise RuntimeError("متغیر BOT_TOKEN در Render تنظیم نشده است.")

    application: Application = (
        ApplicationBuilder()
        .token(TOKEN)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
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
