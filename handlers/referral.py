from aiogram import Router, F
from aiogram.types import Message
from database.db import get_user, get_referrals
from utils.helpers import format_ton
from config import REFERRAL_PERCENTS

router = Router()


@router.message(F.text.in_(["👥 Рефералы", "👥 Referrals"]))
async def show_referral(message: Message, lang: str):
    user_id = message.from_user.id
    user = await get_user(user_id)
    ref_count = await get_referrals(user_id)

    bot_info = await message.bot.get_me()
    link = f"https://t.me/{bot_info.username}?start={user_id}"

    if lang == "ru":
        text = (
            "╔══════════════════════╗\n"
            "║    👥 РЕФЕРАЛЫ       ║\n"
            "╚══════════════════════╝\n\n"
            f"👥 Ваших рефералов: <b>{ref_count}</b>\n"
            f"💰 Заработано: <b>{format_ton(user['ref_earned'])} TON</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "📊 <b>Вознаграждения по уровням:</b>\n"
            "  1️⃣ Уровень — <b>7%</b>\n"
            "  2️⃣ Уровень — <b>3%</b>\n"
            "  3️⃣ Уровень — <b>2%</b>\n"
            "  4️⃣ Уровень — <b>1%</b>\n"
            "  5️⃣ Уровень — <b>0.5%</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "🎁 <b>Бонусы за рефералов:</b>\n"
            "  👤 За приглашение: +<b>0.5 TON</b>\n"
            "  🛒 Купил 1 рабочего: +<b>1 TON</b>\n"
            "  👷 Купил 5 рабочих: +<b>2 TON</b>\n"
            "  🏭 Купил 10 рабочих: +<b>5 TON</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔗 <b>Ваша ссылка:</b>\n<code>{link}</code>"
        )
    else:
        text = (
            "╔══════════════════════╗\n"
            "║    👥 REFERRALS      ║\n"
            "╚══════════════════════╝\n\n"
            f"👥 Your referrals: <b>{ref_count}</b>\n"
            f"💰 Earned: <b>{format_ton(user['ref_earned'])} TON</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "📊 <b>Level rewards:</b>\n"
            "  1️⃣ Level — <b>7%</b>\n"
            "  2️⃣ Level — <b>3%</b>\n"
            "  3️⃣ Level — <b>2%</b>\n"
            "  4️⃣ Level — <b>1%</b>\n"
            "  5️⃣ Level — <b>0.5%</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "🎁 <b>Referral bonuses:</b>\n"
            "  👤 For invite: +<b>0.5 TON</b>\n"
            "  🛒 Bought 1 worker: +<b>1 TON</b>\n"
            "  👷 Bought 5 workers: +<b>2 TON</b>\n"
            "  🏭 Bought 10 workers: +<b>5 TON</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔗 <b>Your link:</b>\n<code>{link}</code>"
        )

    await message.answer(text, parse_mode="HTML")