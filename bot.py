import os

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes


TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", "10000"))
WEBHOOK_URL = "https://clevermindsbot.onrender.com"


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    await update.message.reply_text(
        "💎 به ربات کلاب Clever Minds خوش آمدید!"
    )


def main() -> None:
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN تنظیم نشده است")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="telegram",
        webhook_url=f"{WEBHOOK_URL}/telegram",
    )


if __name__ == "__main__":
    main()
