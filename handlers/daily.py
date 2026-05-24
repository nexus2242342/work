from datetime import date, timedelta
from aiogram import Router, F
from aiogram.types import Message
from database.db import get_user, get_daily_info, update_daily, update_balance
from utils.helpers import format_ton
from config import DAILY_BONUSES

router = Router()


def get_daily_bonus(streak: int) -> float:
    bonus = DAILY_BONUSES.get(1, 0.05)
    for day, amount in sorted(DAILY_BONUSES.items()):
        if streak >= day:
            bonus = amount
    return bonus


def build_streak_bar(streak: int) -> str:
    days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    filled = min(streak % 7, 7)
    bar = ""
    for i in range(7):
        bar += "🟨" if i < filled else "⬜"
    return bar


@router.message(F.text.in_(["🎁 Ежедневный бонус", "🎁 Daily Bonus"]))
async def daily_bonus(message: Message, lang: str):
    user_id = message.from_user.id
    info = await get_daily_info(user_id)
    if not info:
        return

    streak, last_daily = info
    today = date.today()
    bar = build_streak_bar(streak)

    if last_daily:
        last_date = date.fromisoformat(str(last_daily))
        if last_date == today:
            next_bonus = get_daily_bonus(streak + 1)
            if lang == "ru":
                await message.answer(
                    "╔══════════════════════╗\n"
                    "║   🎁 ЕЖЕДНЕВНЫЙ БОНУС ║\n"
                    "╚══════════════════════╝\n\n"
                    "⏰ <b>Вы уже получили бонус сегодня!</b>\n"
                    "Приходите завтра!\n\n"
                    f"🔥 Серия: <b>{streak} дней</b>\n"
                    f"{bar}\n\n"
                    f"💰 Завтра: <b>+{next_bonus} TON</b>",
                    parse_mode="HTML"
                )
            else:
                await message.answer(
                    "╔══════════════════════╗\n"
                    "║    🎁 DAILY BONUS    ║\n"
                    "╚══════════════════════╝\n\n"
                    "⏰ <b>You already claimed today's bonus!</b>\n"
                    "Come back tomorrow!\n\n"
                    f"🔥 Streak: <b>{streak} days</b>\n"
                    f"{bar}\n\n"
                    f"💰 Tomorrow: <b>+{next_bonus} TON</b>",
                    parse_mode="HTML"
                )
            return

        if last_date < today - timedelta(days=1):
            streak = 0

    streak += 1
    bonus = get_daily_bonus(streak)
    await update_daily(user_id, streak)
    await update_balance(user_id, bonus)
    user = await get_user(user_id)
    new_bar = build_streak_bar(streak)
    next_bonus = get_daily_bonus(streak + 1)

    if lang == "ru":
        await message.answer(
            "╔══════════════════════╗\n"
            "║   🎁 ЕЖЕДНЕВНЫЙ БОНУС ║\n"
            "╚══════════════════════╝\n\n"
            "✅ <b>Бонус получен!</b>\n\n"
            f"💰 +<b>{bonus} TON</b>\n"
            f"💳 Баланс: <b>{format_ton(user['balance'])} TON</b>\n\n"
            f"🔥 Серия: <b>{streak} дней</b>\n"
            f"{new_bar}\n\n"
            f"💎 Завтра: <b>+{next_bonus} TON</b>",
            parse_mode="HTML"
        )
    else:
        await message.answer(
            "╔══════════════════════╗\n"
            "║    🎁 DAILY BONUS    ║\n"
            "╚══════════════════════╝\n\n"
            "✅ <b>Bonus claimed!</b>\n\n"
            f"💰 +<b>{bonus} TON</b>\n"
            f"💳 Balance: <b>{format_ton(user['balance'])} TON</b>\n\n"
            f"🔥 Streak: <b>{streak} days</b>\n"
            f"{new_bar}\n\n"
            f"💎 Tomorrow: <b>+{next_bonus} TON</b>",
            parse_mode="HTML"
        )