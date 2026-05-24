from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from database.db import get_user, get_user_workers, update_balance, update_last_collect
from keyboards.kb import workers_keyboard
from utils.helpers import calculate_income, calculate_pending, format_ton, get_worker_name
from config import WORKERS

router = Router()


@router.message(F.text.in_(["👷 Мои рабочие", "👷 My Workers"]))
async def show_workers(message: Message, lang: str):
    user_id = message.from_user.id
    user = await get_user(user_id)
    workers = await get_user_workers(user_id)
    income = await calculate_income(user_id)
    pending = await calculate_pending(user_id)

    if lang == "ru":
        header = (
            "╔══════════════════════╗\n"
            "║    👷 МОИ РАБОЧИЕ    ║\n"
            "╚══════════════════════╝\n\n"
            f"💰 Баланс: <b>{format_ton(user['balance'])} TON</b>\n"
            f"📈 Доход/день: <b>{format_ton(income)} TON</b>\n"
            f"⏳ Накоплено: <b>{format_ton(pending)} TON</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "📋 Список рабочих:\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
        )
    else:
        header = (
            "╔══════════════════════╗\n"
            "║    👷 MY WORKERS     ║\n"
            "╚══════════════════════╝\n\n"
            f"💰 Balance: <b>{format_ton(user['balance'])} TON</b>\n"
            f"📈 Income/day: <b>{format_ton(income)} TON</b>\n"
            f"⏳ Pending: <b>{format_ton(pending)} TON</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "📋 Workers list:\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
        )

    if not workers:
        no_workers = (
            "😔 У вас нет рабочих.\nЗайдите в магазин!"
            if lang == "ru"
            else "😔 You have no workers.\nGo to the shop!"
        )
        await message.answer(header + no_workers, parse_mode="HTML")
        return

    lines = []
    for w in workers:
        wtype = w["worker_type"]
        cnt = w["cnt"]
        name = get_worker_name(wtype, lang)
        day_income = WORKERS[wtype]["income_day"] * cnt
        lines.append(f"  {name} ×{cnt}\n  └ {day_income:.4f} TON/day")

    await message.answer(
        header + "\n".join(lines),
        reply_markup=workers_keyboard(lang),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "collect_income")
async def collect_income(callback: CallbackQuery, lang: str):
    user_id = callback.from_user.id
    pending = await calculate_pending(user_id)

    if pending < 0.0001:
        await callback.answer(
            "⏰ Ещё нечего собирать!" if lang == "ru" else "⏰ Nothing to collect yet!",
            show_alert=True
        )
        return

    await update_balance(user_id, pending)
    await update_last_collect(user_id)
    user = await get_user(user_id)

    await callback.message.edit_text(
        f"✅ <b>{'Доход собран!' if lang == 'ru' else 'Income collected!'}</b>\n\n"
        f"💰 +<b>{format_ton(pending)} TON</b>\n"
        f"{'Баланс' if lang == 'ru' else 'Balance'}: <b>{format_ton(user['balance'])} TON</b>",
        parse_mode="HTML"
    )
    await callback.answer()