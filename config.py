import os
from typing import Final

TOKEN: Final[str] = os.getenv("BOT_TOKEN", "")
PORT: Final[int] = int(os.getenv("PORT", "10000"))
WEBHOOK_URL: Final[str] = os.getenv(
    "WEBHOOK_URL",
    "https://clevermindsbot.onrender.com",
)
