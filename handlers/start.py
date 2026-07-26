from telegram import Update
from telegram.ext import ContextTypes

from keyboards.menus import main_menu
from storage import user_states


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_states.pop(user.id, None)

    await update.message.reply_text(
        text=(
            f"سلام <b>{user.first_name}</b> 💎\n\n"
            f"به <b>Clever Minds Mafia</b> خوش آمدی.\n\n"
            "یکی از گزینه‌های زیر را انتخاب کن:"
        ),
        reply_markup=main_menu(),
        parse_mode="HTML",
    )
