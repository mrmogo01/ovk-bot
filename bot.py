"""Telegram-бот: по команде /ovk пишет, сколько осталось до ОВК."""

import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from telegram import BotCommand, Update
from telegram.ext import Application, CommandHandler, ContextTypes

load_dotenv()

OVK_AT = os.getenv("OVK_AT", "2026-11-27T17:00:00")
OVK_TZ = os.getenv("OVK_TZ", "Asia/Yekaterinburg")
TZ = ZoneInfo(OVK_TZ)
TARGET = datetime.fromisoformat(OVK_AT).replace(tzinfo=TZ)


def ru_plural(n: int, one: str, few: str, many: str) -> str:
    n = abs(n) % 100
    if 11 <= n <= 14:
        return many
    last = n % 10
    if last == 1:
        return one
    if 2 <= last <= 4:
        return few
    return many


def format_remaining(now: datetime) -> str:
    total = int((TARGET - now).total_seconds())
    if total <= 0:
        return "ОВК уже началось."
    days, rem = divmod(total, 24 * 60 * 60)
    hours, rem = divmod(rem, 60 * 60)
    minutes = rem // 60
    return (
        f"До овк осталось {days} {ru_plural(days, 'день', 'дня', 'дней')} "
        f"{hours} {ru_plural(hours, 'час', 'часа', 'часов')} "
        f"{minutes} {ru_plural(minutes, 'минута', 'минуты', 'минут')}"
    )


async def ovk(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if message is None:
        return
    await message.reply_text(format_remaining(datetime.now(TZ)))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if message is None:
        return
    await message.reply_text("Напиши /ovk — скажу, сколько осталось до ОВК.")


async def post_init(app: Application) -> None:
    await app.bot.set_my_commands([BotCommand("ovk", "Сколько осталось до ОВК")])


def main() -> None:
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        print("Нет BOT_TOKEN. Создай бота у @BotFather и положи токен в ovk-bot/.env", file=sys.stderr)
        sys.exit(1)

    app = Application.builder().token(token).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ovk", ovk))
    print(f"Бот запущен. ОВК: {TARGET.strftime('%d.%m.%Y %H:%M')} ({OVK_TZ})")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
