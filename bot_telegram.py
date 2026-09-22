"""Bot da Antena Hair para Telegram.

Uso:
    export TELEGRAM_BOT_TOKEN="token recebido no BotFather"
    python bot_telegram.py

O bot funciona só com o token do Telegram. A integração opcional com Gemini
é ativada quando GEMINI_API_KEY estiver definida.
"""
from __future__ import annotations

import asyncio
import logging
import os

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from salon_logic import SalonBot

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

logic = SalonBot()
gemini = None


def maybe_load_gemini():
    if not os.environ.get("GEMINI_API_KEY"):
        return None
    try:
        from gemini_client import GeminiClient
        return GeminiClient()
    except Exception as exc:  # não impede o fluxo principal
        logger.warning("Gemini opcional não foi ativado: %s", exc)
        return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user and update.message:
        await update.message.reply_text(
            logic.reset(update.effective_user.id), parse_mode="Markdown"
        )


async def message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_user or not update.message or not update.message.text:
        return

    user_id = update.effective_user.id
    text = update.message.text
    response = logic.respond(user_id, text)

    # O fluxo de preços/agendamento é determinístico para não inventar valores.
    # O Gemini fica reservado para perguntas gerais que não sejam reconhecidas.
    if response.startswith("Não consegui identificar") and gemini is not None:
        response = await asyncio.to_thread(gemini.answer, text)

    await update.message.reply_text(response, parse_mode="Markdown")


def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit("Erro: defina TELEGRAM_BOT_TOKEN antes de executar.")

    global gemini
    gemini = maybe_load_gemini()

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message))
    logger.info("Bot iniciado. Use Ctrl+C para parar.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
