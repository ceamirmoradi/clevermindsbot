import logging

from telegram import Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from engine.game_service import (
    add_pending_player,
    approve_player,
    approved_players,
    create_game,
    generate_game_code,
    get_player,
    reject_player,
    randomize_seats,
    transfer_narrator,
)
from keyboards.menus import (
    back_to_home_menu,
    confirm_scenario_menu,
    main_menu,
    scenarios_menu,
)
from keyboards.narrator import (
    narrator_lobby_menu,
    player_actions_menu,
    players_management_menu,
    transfer_menu,
)
from scenarios import SCENARIOS
from storage import games, user_states
from views import narrator_lobby_text, player_detail_text

logger = logging.getLogger(__name__)


async def safe_edit_lobby(
    context: ContextTypes.DEFAULT_TYPE,
    game: dict,
) -> None:
    try:
        await context.bot.edit_message_text(
            chat_id=game["narrator_chat_id"],
            message_id=game["lobby_message_id"],
            text=narrator_lobby_text(game),
            reply_markup=narrator_lobby_menu(game["code"]),
            parse_mode="HTML",
        )
    except BadRequest as exc:
        if "Message is not modified" not in str(exc):
            logger.warning("Could not edit lobby: %s", exc)
    except Exception as exc:
        logger.warning("Could not edit lobby: %s", exc)


async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query
    user = query.from_user
    action = query.data
    await query.answer()

    if action == "home":
        user_states.pop(user.id, None)
        await query.edit_message_text(
            "💎 <b>منوی اصلی Clever Minds</b>",
            reply_markup=main_menu(),
            parse_mode="HTML",
        )
        return

    if action == "create_game":
        await query.edit_message_text(
            "🎭 <b>انتخاب سناریو</b>",
            reply_markup=scenarios_menu(),
            parse_mode="HTML",
        )
        return

    if action.startswith("scenario:"):
        scenario_id = action.split(":", 1)[1]
        scenario = SCENARIOS.get(scenario_id)
        if not scenario:
            await query.edit_message_text("❌ سناریو پیدا نشد.")
            return

        await query.edit_message_text(
            text=(
                f"{scenario['emoji']} <b>{scenario['name']}</b>\n\n"
                f"👥 {scenario['player_count']} نفر\n"
                f"📝 {scenario['description']}"
            ),
            reply_markup=confirm_scenario_menu(scenario_id),
            parse_mode="HTML",
        )
        return

    if action.startswith("confirm_scenario:"):
        scenario_id = action.split(":", 1)[1]
        scenario = SCENARIOS.get(scenario_id)
        if not scenario:
            await query.edit_message_text("❌ سناریو معتبر نیست.")
            return

        for code, game in games.items():
            if (
                game["narrator_id"] == user.id
                and game["status"] in {"waiting", "running"}
            ):
                await query.edit_message_text(
                    narrator_lobby_text(game),
                    reply_markup=narrator_lobby_menu(code),
                    parse_mode="HTML",
                )
                game["narrator_chat_id"] = query.message.chat_id
                game["lobby_message_id"] = query.message.message_id
                return

        code = generate_game_code()
        # ابتدا همان پیام را تبدیل به پنل می‌کنیم.
        placeholder = {
            "code": code,
            "scenario_id": scenario_id,
            "narrator_id": user.id,
            "narrator_name": user.first_name,
            "players": [],
            "max_players": scenario["player_count"],
            "registration_open": True,
            "status": "waiting",
        }
        await query.edit_message_text(
            narrator_lobby_text(placeholder),
            reply_markup=narrator_lobby_menu(code),
            parse_mode="HTML",
        )

        create_game(
            code=code,
            scenario_id=scenario_id,
            narrator_id=user.id,
            narrator_name=user.first_name,
            narrator_chat_id=query.message.chat_id,
            lobby_message_id=query.message.message_id,
        )
        return

    if action == "join_game":
        user_states[user.id] = "waiting_for_game_code"
        await query.edit_message_text(
            "🎮 کد چهاررقمی بازی را ارسال کن.",
            reply_markup=back_to_home_menu(),
        )
        return

    if action.startswith("confirm_join:"):
        code = action.split(":", 1)[1]
        game = games.get(code)
        if not game:
            await query.edit_message_text("❌ بازی فعال نیست.")
            return
        if not game["registration_open"]:
            await query.edit_message_text("🔒 ثبت‌نام بسته است.")
            return
        if user.id == game["narrator_id"]:
            await query.answer(
                "گرداننده نمی‌تواند به‌عنوان بازیکن وارد همان بازی شود.",
                show_alert=True,
            )
            return

        player = add_pending_player(
            game,
            user_id=user.id,
            name=user.first_name,
            username=user.username,
        )
        user_states.pop(user.id, None)

        await query.edit_message_text(
            text=(
                "⏳ <b>درخواست ورود ثبت شد</b>\n\n"
                "پس از تأیید گرداننده، شماره صندلی در زمان قرعه‌کشی مشخص می‌شود."
            ),
            reply_markup=back_to_home_menu(),
            parse_mode="HTML",
        )
        await safe_edit_lobby(context, game)
        return

    # تمام گزینه‌های بعدی مخصوص گرداننده‌اند.
    if ":" in action:
        parts = action.split(":")
        code = parts[1] if len(parts) > 1 else ""
        game = games.get(code)
    else:
        game = None

    if action.startswith(
        (
            "refresh_game:",
            "players:",
            "player:",
            "approve:",
            "reject:",
            "transfer_menu:",
            "transfer_confirm:",
            "close_registration:",
            "randomize_seats:",
            "start_game:",
            "cancel_game:",
        )
    ):
        if not game:
            await query.edit_message_text("❌ بازی پیدا نشد.")
            return
        if game["narrator_id"] != user.id:
            await query.answer(
                "فقط گرداننده فعلی به این بخش دسترسی دارد.",
                show_alert=True,
            )
            return

    if action.startswith("refresh_game:"):
        await query.edit_message_text(
            narrator_lobby_text(game),
            reply_markup=narrator_lobby_menu(game["code"]),
            parse_mode="HTML",
        )
        game["narrator_chat_id"] = query.message.chat_id
        game["lobby_message_id"] = query.message.message_id
        return

    if action.startswith("players:"):
        await query.edit_message_text(
            text=f"👥 <b>مدیریت بازیکنان بازی {game['code']}</b>",
            reply_markup=players_management_menu(
                game["code"],
                game["players"],
            ),
            parse_mode="HTML",
        )
        return

    if action.startswith("player:"):
        _, code, raw_user_id = action.split(":")
        player = get_player(game, int(raw_user_id))
        if not player:
            await query.edit_message_text("❌ بازیکن پیدا نشد.")
            return
        await query.edit_message_text(
            player_detail_text(player),
            reply_markup=player_actions_menu(code, player["user_id"]),
            parse_mode="HTML",
        )
        return

    if action.startswith("approve:"):
        _, code, raw_user_id = action.split(":")
        try:
            player = approve_player(game, int(raw_user_id))
        except ValueError as exc:
            await query.answer(str(exc), show_alert=True)
            return

        await query.answer(f"{player['name']} تأیید شد.", show_alert=True)
        try:
            await context.bot.send_message(
                chat_id=player["user_id"],
                text=(
                    "✅ <b>ورود شما به میز بازی تأیید شد</b>\n\n"
                    f"🔑 کد بازی: <code>{code}</code>\n"
                    "🪑 شماره صندلی پس از بسته‌شدن ثبت‌نام و قرعه‌کشی اعلام می‌شود."
                ),
                parse_mode="HTML",
            )
        except Exception:
            pass

        await query.edit_message_text(
            "👥 <b>مدیریت بازیکنان</b>",
            reply_markup=players_management_menu(code, game["players"]),
            parse_mode="HTML",
        )
        await safe_edit_lobby(context, game)
        return

    if action.startswith("reject:"):
        _, code, raw_user_id = action.split(":")
        try:
            player = reject_player(game, int(raw_user_id))
        except ValueError as exc:
            await query.answer(str(exc), show_alert=True)
            return

        try:
            await context.bot.send_message(
                chat_id=player["user_id"],
                text="❌ درخواست ورود شما توسط گرداننده رد شد.",
            )
        except Exception:
            pass

        await query.edit_message_text(
            "👥 <b>مدیریت بازیکنان</b>",
            reply_markup=players_management_menu(code, game["players"]),
            parse_mode="HTML",
        )
        await safe_edit_lobby(context, game)
        return

    if action.startswith("transfer_menu:"):
        approved = approved_players(game)
        if not approved:
            await query.answer(
                "ابتدا باید حداقل یک بازیکن تأیید شده باشد.",
                show_alert=True,
            )
            return
        await query.edit_message_text(
            "👑 <b>گرداننده جدید را انتخاب کن</b>",
            reply_markup=transfer_menu(game["code"], game["players"]),
            parse_mode="HTML",
        )
        return

    if action.startswith("transfer_confirm:"):
        _, code, raw_user_id = action.split(":")
        player = get_player(game, int(raw_user_id))
        if not player or player["status"] != "approved":
            await query.answer(
                "فقط یک بازیکن تأییدشده می‌تواند گرداننده شود.",
                show_alert=True,
            )
            return

        old_narrator_id = game["narrator_id"]
        transfer_narrator(
            game,
            new_narrator_id=player["user_id"],
            new_narrator_name=player["name"],
        )

        # گرداننده جدید دیگر بازیکن محسوب نمی‌شود.
        game["players"] = [
            p for p in game["players"]
            if p["user_id"] != player["user_id"]
        ]

        await query.edit_message_text(
            text=(
                "✅ گردانندگی منتقل شد.\n\n"
                f"گرداننده جدید: <b>{player['name']}</b>"
            ),
            reply_markup=back_to_home_menu(),
            parse_mode="HTML",
        )

        try:
            msg = await context.bot.send_message(
                chat_id=player["user_id"],
                text=narrator_lobby_text(game),
                reply_markup=narrator_lobby_menu(code),
                parse_mode="HTML",
            )
            game["narrator_chat_id"] = msg.chat_id
            game["lobby_message_id"] = msg.message_id
        except Exception as exc:
            logger.warning("Could not send new narrator panel: %s", exc)

        await safe_edit_lobby(context, game)
        return

    if action.startswith("close_registration:"):
        game["registration_open"] = False
        if approved_players(game):
            randomize_seats(game)
            for player in approved_players(game):
                try:
                    await context.bot.send_message(
                        chat_id=player["user_id"],
                        text=(
                            "🎲 <b>قرعه‌کشی صندلی‌ها انجام شد</b>\n\n"
                            f"🔑 کد بازی: <code>{game['code']}</code>\n"
                            f"🪑 شماره صندلی شما: <b>{player['seat']}</b>"
                        ),
                        parse_mode="HTML",
                    )
                except Exception:
                    pass
        await query.edit_message_text(
            narrator_lobby_text(game),
            reply_markup=narrator_lobby_menu(game["code"]),
            parse_mode="HTML",
        )
        return

    if action.startswith("randomize_seats:"):
        if game["registration_open"]:
            await query.answer(
                "ابتدا ثبت‌نام را ببند تا فهرست بازیکنان نهایی شود.",
                show_alert=True,
            )
            return
        try:
            randomize_seats(game)
        except ValueError as exc:
            await query.answer(str(exc), show_alert=True)
            return
        for player in approved_players(game):
            try:
                await context.bot.send_message(
                    chat_id=player["user_id"],
                    text=(
                        "🔄 <b>صندلی‌ها دوباره قرعه‌کشی شدند</b>\n\n"
                        f"🔑 کد بازی: <code>{game['code']}</code>\n"
                        f"🪑 شماره صندلی جدید شما: <b>{player['seat']}</b>"
                    ),
                    parse_mode="HTML",
                )
            except Exception:
                pass
        await query.edit_message_text(
            narrator_lobby_text(game),
            reply_markup=narrator_lobby_menu(game["code"]),
            parse_mode="HTML",
        )
        return

    if action.startswith("start_game:"):
        count = len(approved_players(game))
        if count != game["max_players"]:
            await query.answer(
                f"برای شروع باید دقیقاً {game['max_players']} بازیکن تأیید شوند. فعلاً {count} نفر تأیید شده‌اند.",
                show_alert=True,
            )
            return
        game["registration_open"] = False
        if not game.get("seats_randomized"):
            randomize_seats(game)
        game["status"] = "running"
        await query.edit_message_text(
            "▶️ <b>بازی شروع شد</b>\n\nمرحله بعد: تقسیم نقش‌ها",
            reply_markup=narrator_lobby_menu(game["code"]),
            parse_mode="HTML",
        )
        return

    if action.startswith("cancel_game:"):
        del games[game["code"]]
        await query.edit_message_text(
            "❌ بازی لغو شد.",
            reply_markup=main_menu(),
        )
        return

    if action == "profile":
        await query.edit_message_text(
            text=(
                "👤 <b>پروفایل شما</b>\n\n"
                f"نام: <b>{user.first_name}</b>\n"
                f"شناسه: <code>{user.id}</code>"
            ),
            reply_markup=back_to_home_menu(),
            parse_mode="HTML",
        )
        return

    if action == "help":
        await query.edit_message_text(
            text=(
                "📚 <b>راهنما</b>\n\n"
                "گرداننده بازی می‌سازد و کد را به بازیکنان می‌دهد.\n"
                "بازیکنان درخواست ورود می‌فرستند و گرداننده آن‌ها را تأیید می‌کند."
            ),
            reply_markup=back_to_home_menu(),
            parse_mode="HTML",
        )
