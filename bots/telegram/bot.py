"""
Telegram bot powered by Claude API.
Run: python bot.py
"""

import os
import logging
from dotenv import load_dotenv
from anthropic import Anthropic
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
ALLOWED_USER_IDS = set(
    int(uid.strip())
    for uid in os.getenv("ALLOWED_USER_IDS", "").split(",")
    if uid.strip()
)

SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "You are a helpful assistant. Reply concisely.")

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

client = Anthropic(api_key=ANTHROPIC_API_KEY)

# 대화 히스토리: {chat_id: [{"role": ..., "content": ...}]}
histories: dict[int, list[dict]] = {}

MAX_HISTORY = 20  # 최대 유지할 메시지 수


def is_allowed(user_id: int) -> bool:
    if not ALLOWED_USER_IDS:
        return True  # 화이트리스트 미설정 시 전체 허용
    return user_id in ALLOWED_USER_IDS


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("안녕하세요. 무엇을 도와드릴까요?")


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    histories.pop(chat_id, None)
    await update.message.reply_text("대화 기록을 초기화했습니다.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    chat_id = update.effective_chat.id

    if not is_allowed(user.id):
        await update.message.reply_text("접근 권한이 없습니다.")
        return

    user_text = update.message.text
    if not user_text:
        return

    history = histories.setdefault(chat_id, [])
    history.append({"role": "user", "content": user_text})

    # 히스토리 크기 제한
    if len(history) > MAX_HISTORY:
        history[:] = history[-MAX_HISTORY:]

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=history,
        )
        reply = response.content[0].text
        history.append({"role": "assistant", "content": reply})
        await update.message.reply_text(reply)
    except Exception as e:
        logger.error("Claude API error: %s", e)
        await update.message.reply_text("오류가 발생했습니다. 잠시 후 다시 시도해주세요.")


def main() -> None:
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot started. Polling...")
    app.run_polling()


if __name__ == "__main__":
    main()
