from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from database.db import get_user, get_referrals, get_achievements, get_top_earned, get_top_refs
from keyboards.kb import stats_keyboard
from utils.helpers import format_ton
from config import ACHIEVEMENTS

router = Router()

MEDALS = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]


@router.message(F.text.in_(["📊 Статистика", "📊 Statistics"]))
async def show_stats(message: Message, lang: str):
    user_id = message.from_user.id
    user = await get_user(user_id)
    refs = await get_referrals(user_id)
    achs = await get_achievements(user_id)

    if lang == "ru":
        text = (
            "╔══════════════════════╗\n"
            "║    📊 СТАТИСТИКА      ║\n"
            "╚══════════════════════╝\n\n"
            f"👤 <b>{user['full_name']}</b>\n\n"
            f"💰 Баланс: <b>{format_ton(user['balance'])} TON</b>\n"
            f"💎 Всего заработано: <b>{format_ton(user['total_earned'])} TON</b>\n"
            f"👷 Рабочих куплено: <b>{user['total_workers']}</b>\n"
            f"🌾 Уровень фермы: <b>{user['farm_level']}/10</b>\n"
            f"🔥 Серия входов: <b>{user['daily_streak']} дней</b>\n"
            f"👥 Рефералов: <b>{refs}</b>\n"
            f"🏅 Достижений: <b>{len(achs)}/4</b>"
        )
    else:
        text = (
            "╔══════════════════════╗\n"
            "║    📊 STATISTICS     ║\n"
            "╚══════════════════════╝\n\n"
            f"👤 <b>{user['full_name']}</b>\n\n"
            f"💰 Balance: <b>{format_ton(user['balance'])} TON</b>\n"
            f"💎 Total earned: <b>{format_ton(user['total_earned'])} TON</b>\n"
            f"👷 Workers bought: <b>{user['total_workers']}</b>\n"
            f"🌾 Farm level: <b>{user['farm_level']}/10</b>\n"
            f"🔥 Login streak: <b>{user['daily_streak']} days</b>\n"
            f"👥 Referrals: <b>{refs}</b>\n"
            f"🏅 Achievements: <b>{len(achs)}/4</b>"
        )

    await message.answer(text, reply_markup=stats_keyboard(lang), parse_mode="HTML")


@router.callback_query(F.data == "show_top")
async def show_top(callback: CallbackQuery, lang: str):
    top_earned = await get_top_earned()
    top_refs = await get_top_refs()

    if lang == "ru":
        text = (
            "╔══════════════════════╗\n"
            "║    🏆 ТОП ИГРОКОВ    ║\n"
            "╚══════════════════════╝\n\n"
            "💰 <b>По заработку:</b>\n"
        )
        for i, row in enumerate(top_earned):
            text += f"{MEDALS[i]} {row['full_name']} — <b>{format_ton(row['total_earned'])} TON</b>\n"

        text += "\n👥 <b>По рефералам:</b>\n"
        for i, row in enumerate(top_refs):
            text += f"{MEDALS[i]} {row['full_name']} — <b>{row['ref_count']} чел.</b>\n"
    else:
        text = (
            "╔══════════════════════╗\n"
            "║    🏆 TOP PLAYERS    ║\n"
            "╚══════════════════════╝\n\n"
            "💰 <b>By earnings:</b>\n"
        )
        for i, row in enumerate(top_earned):
            text += f"{MEDALS[i]} {row['full_name']} — <b>{format_ton(row['total_earned'])} TON</b>\n"

        text += "\n👥 <b>By referrals:</b>\n"
        for i, row in enumerate(top_refs):
            text += f"{MEDALS[i]} {row['full_name']} — <b>{row['ref_count']} people</b>\n"

    await callback.message.edit_text(text, reply_markup=stats_keyboard(lang), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "show_achievements")
async def show_achievements(callback: CallbackQuery, lang: str):
    user_id = callback.from_user.id
    done = await get_achievements(user_id)

    if lang == "ru":
        text = (
            "╔══════════════════════╗\n"
            "║    🏅 ДОСТИЖЕНИЯ     ║\n"
            "╚══════════════════════╝\n\n"
        )
    else:
        text = (
            "╔══════════════════════╗\n"
            "║    🏅 ACHIEVEMENTS   ║\n"
            "╚══════════════════════╝\n\n"
        )

    for key, data in ACHIEVEMENTS.items():
        name = data.get(f"name_{lang}", data["name_ru"])
        title = data.get(f"title_{lang}", data["title_ru"])
        if key in done:
            text += (
                f"✅ <b>{name}</b>\n"
                f"  👑 {title} | 💰 +{data['reward']} TON\n\n"
            )
        else:
            text += (
                f"🔒 <b>{name}</b>\n"
                f"  💰 +{data['reward']} TON\n\n"
            )

    await callback.message.edit_text(text, reply_markup=stats_keyboard(lang), parse_mode="HTML")
    await callback.answer()