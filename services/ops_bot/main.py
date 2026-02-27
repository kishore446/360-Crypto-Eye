from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from libs.core.config import settings
from libs.core.logging import get_logger
from libs.adapters.telegram_adapter import TelegramAdapter

logger = get_logger("ops_bot")


def is_admin(update: Update) -> bool:
    user = update.effective_user
    return bool(user and user.id == settings.telegram_admin_user_id)


async def admin_only(update: Update) -> bool:
    if not is_admin(update):
        if update.message:
            await update.message.reply_text("❌ Unauthorized")
        return False
    return True


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await admin_only(update):
        return
    await update.message.reply_text("pong ✅ ops-bot alive")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await admin_only(update):
        return
    await update.message.reply_text("Status:\\n- ops-bot: healthy")


async def post_spot_test(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await admin_only(update):
        return
    t = TelegramAdapter()
    await t.send_text("spot", "📍 BTCUSDT (SPOT) — 1h\\nBias: Bullish (62%)\\nSpot test post ✅")
    await update.message.reply_text("Posted to SPOT channel ✅")


async def post_futures_test(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await admin_only(update):
        return
    t = TelegramAdapter()
    await t.send_text("futures", "📍 BTCUSDT (FUTURES) — 1h\\nBias: Neutral (51%)\\nFutures test post ✅")
    await update.message.reply_text("Posted to FUTURES channel ✅")


def main() -> None:
    app = Application.builder().token(settings.telegram_bot_token).build()
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("post_spot_test", post_spot_test))
    app.add_handler(CommandHandler("post_futures_test", post_futures_test))
    logger.info("Starting ops bot...")
    app.run_polling()


if __name__ == "__main__":
    main()
