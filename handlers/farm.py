from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from database.db import get_user, get_worker_count, update_balance, update_farm_level
from keyboards.kb import farm_keyboard
from utils.helpers import format_ton
from config import FARM_LEVELS, FARM_MILESTONES

router = Router()


async def build_farm_text(user_id: int, lang: str) -> tuple:
    from database.db import get_user
    user = await get_user(user_id)
    level = user["farm_level"]
    worker_count = await get_worker_count(user_id)
    farm_data = FARM_LEVELS[level]
    is_max = level >= 10

    stars = "⭐" * level + "☆" * (10 - level)

    if is_max:
        if lang == "ru":
            text = (
                "╔══════════════════════╗\n"
                "║    🌾 ВАША ФЕРМА     ║\n"
                "╚══════════════════════╝\n\n"
                f"📊 Уровень: <b>MAX (10/10)</b>\n"
                f"{stars}\n\n"
                f"👷 Рабочих: <b>{worker_count}</b>\n"
                f"🎁 Бонус фермы: <b>+{int(farm_data['bonus'] * 100)}%</b>\n\n"
                "🏆 <b>Ферма полностью прокачана!</b>"
            )
        else:
            text = (
                "╔══════════════════════╗\n"
                "║      🌾 YOUR FARM    ║\n"
                "╚══════════════════════╝\n\n"
                f"📊 Level: <b>MAX (10/10)</b>\n"
                f"{stars}\n\n"
                f"👷 Workers: <b>{worker_count}</b>\n"
                f"🎁 Farm bonus: <b>+{int(farm_data['bonus'] * 100)}%</b>\n\n"
                "🏆 <b>Farm is fully upgraded!</b>"
            )
        return text, True, 0

    next_data = FARM_LEVELS[level + 1]
    cost = next_data["upgrade_cost"]
    need_workers = next_data["min_workers"]
    can_upgrade = worker_count >= need_workers and user["balance"] >= cost

    progress = min(int((worker_count / max(need_workers, 1)) * 10), 10)
    progress_bar = "🟦" * progress + "⬜" * (10 - progress)

    if lang == "ru":
        text = (
            "╔══════════════════════╗\n"
            "║    🌾 ВАША ФЕРМА     ║\n"
            "╚══════════════════════╝\n\n"
            f"📊 Уровень: <b>{level}/10</b>\n"
            f"{stars}\n\n"
            f"👷 Рабочих: <b>{worker_count}</b>\n"
            f"🎁 Бонус: <b>+{int(farm_data['bonus'] * 100)}%</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⬆️ <b>Следующий уровень:</b>\n"
            f"💰 Стоимость: <b>{cost} TON</b>\n"
            f"👷 Нужно рабочих: <b>{need_workers}</b>\n"
            f"🎁 Новый бонус: <b>+{int(next_data['bonus'] * 100)}%</b>\n\n"
            f"Прогресс рабочих:\n{progress_bar} {worker_count}/{need_workers}"
        )
    else:
        text = (
            "╔══════════════════════╗\n"
            "║      🌾 YOUR FARM    ║\n"
            "╚══════════════════════╝\n\n"
            f"📊 Level: <b>{level}/10</b>\n"
            f"{stars}\n\n"
            f"👷 Workers: <b>{worker_count}</b>\n"
            f"🎁 Bonus: <b>+{int(farm_data['bonus'] * 100)}%</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⬆️ <b>Next level:</b>\n"
            f"💰 Cost: <b>{cost} TON</b>\n"
            f"👷 Workers needed: <b>{need_workers}</b>\n"
            f"🎁 New bonus: <b>+{int(next_data['bonus'] * 100)}%</b>\n\n"
            f"Workers progress:\n{progress_bar} {worker_count}/{need_workers}"
        )

    return text, is_max, cost


@router.message(F.text.in_(["🌾 Ферма", "🌾 Farm"]))
async def show_farm(message: Message, lang: str):
    user_id = message.from_user.id
    user = await get_user(user_id)
    worker_count = await get_worker_count(user_id)
    level = user["farm_level"]
    is_max = level >= 10

    text, is_max, cost = await build_farm_text(user_id, lang)
    can_upgrade = False
    if not is_max:
        next_data = FARM_LEVELS[level + 1]
        can_upgrade = (
            worker_count >= next_data["min_workers"] and
            user["balance"] >= next_data["upgrade_cost"]
        )

    await message.answer(
        text,
        reply_markup=farm_keyboard(can_upgrade, cost, is_max, lang),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "upgrade_farm")
async def upgrade_farm(callback: CallbackQuery, lang: str):
    user_id = callback.from_user.id
    user = await get_user(user_id)
    level = user["farm_level"]
    worker_count = await get_worker_count(user_id)

    if level >= 10:
        await callback.answer("Max!" , show_alert=True)
        return

    next_data = FARM_LEVELS[level + 1]
    cost = next_data["upgrade_cost"]

    if worker_count < next_data["min_workers"]:
        await callback.answer(
            f"❌ {'Нужно минимум' if lang == 'ru' else 'Need at least'} "
            f"{next_data['min_workers']} {'рабочих!' if lang == 'ru' else 'workers!'}",
            show_alert=True
        )
        return

    if user["balance"] < cost:
        await callback.answer(
            f"❌ {'Недостаточно средств!' if lang == 'ru' else 'Not enough funds!'}\n"
            f"{'Нужно' if lang == 'ru' else 'Need'}: {cost} TON",
            show_alert=True
        )
        return

    new_level = level + 1
    await update_balance(user_id, -cost)
    await update_farm_level(user_id, new_level)

    new_bonus = FARM_LEVELS[new_level]["bonus"]
    await callback.message.edit_text(
        f"🎉 <b>{'Ферма улучшена!' if lang == 'ru' else 'Farm upgraded!'}</b>\n\n"
        f"📊 {'Уровень' if lang == 'ru' else 'Level'}: <b>{new_level}/10</b>\n"
        f"🎁 {'Бонус' if lang == 'ru' else 'Bonus'}: <b>+{int(new_bonus * 100)}%</b>",
        parse_mode="HTML"
    )

    if worker_count in FARM_MILESTONES:
        bonus = FARM_MILESTONES[worker_count]
        await update_balance(user_id, bonus)
        await callback.message.answer(
            f"🎉 <b>{'Веха фермы!' if lang == 'ru' else 'Farm Milestone!'}</b>\n\n"
            f"+<b>{bonus} TON</b> {'за' if lang == 'ru' else 'for'} "
            f"<b>{worker_count}</b> {'рабочих!' if lang == 'ru' else 'workers!'}",
            parse_mode="HTML"
        )
    await callback.answer()