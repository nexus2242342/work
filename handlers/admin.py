from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
import aiosqlite
from database.db import (get_withdrawal, update_withdrawal_status,
                          update_balance, get_user)
from keyboards.kb import admin_keyboard
from utils.helpers import format_ton
from config import ADMIN_IDS, SUPPORT_USERNAME

router = Router()


class AdminFSM(StatesGroup):
    waiting_uid = State()
    waiting_amount = State()


@router.message(Command("admin"))
async def admin_panel(message: Message, lang: str):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ Нет доступа." if lang == "ru" else "❌ No access.")
        return

    await message.answer(
        "╔══════════════════════╗\n"
        "║  👑 ПАНЕЛЬ АДМИНА   ║\n"
        "╚══════════════════════╝\n\n"
        f"{'Выберите действие:' if lang == 'ru' else 'Choose action:'}",
        reply_markup=admin_keyboard(lang),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("admin_approve_"))
async def approve_withdraw(callback: CallbackQuery, bot: Bot):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("No access", show_alert=True)
        return

    withdraw_id = int(callback.data.split("_")[2])
    w = await get_withdrawal(withdraw_id)
    if not w or w["status"] != "pending":
        await callback.answer("Already processed", show_alert=True)
        return

    await update_withdrawal_status(withdraw_id, "approved")
    await callback.message.edit_text(
        f"✅ <b>Вывод одобрен!</b>\n\n"
        f"💰 {format_ton(w['amount'])} TON → <code>{w['address']}</code>",
        parse_mode="HTML"
    )

    try:
        await bot.send_message(
            w["user_id"],
            f"✅ <b>Ваш вывод одобрен!</b>\n\n"
            f"💰 {format_ton(w['amount'])} TON отправлено на\n"
            f"<code>{w['address']}</code>",
            parse_mode="HTML"
        )
    except Exception:
        pass
    await callback.answer("✅ Одобрено")


@router.callback_query(F.data.startswith("admin_reject_"))
async def reject_withdraw(callback: CallbackQuery, bot: Bot):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("No access", show_alert=True)
        return

    withdraw_id = int(callback.data.split("_")[2])
    w = await get_withdrawal(withdraw_id)
    if not w or w["status"] != "pending":
        await callback.answer("Already processed", show_alert=True)
        return

    await update_withdrawal_status(withdraw_id, "rejected")
    await update_balance(w["user_id"], w["amount"])
    await callback.message.edit_text("❌ <b>Вывод отклонён. Средства возвращены.</b>", parse_mode="HTML")

    try:
        await bot.send_message(
            w["user_id"],
            f"❌ <b>Вывод отклонён</b>\n\n"
            f"💰 {format_ton(w['amount'])} TON возвращено на баланс\n"
            f"📩 Поддержка: {SUPPORT_USERNAME}",
            parse_mode="HTML"
        )
    except Exception:
        pass
    await callback.answer("❌ Отклонено")


@router.callback_query(F.data == "admin_add_balance")
async def admin_add_balance_start(callback: CallbackQuery, state: FSMContext, lang: str):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("No access", show_alert=True)
        return
    await callback.message.edit_text(
        "💰 Введите ID пользователя:" if lang == "ru" else "💰 Enter user ID:"
    )
    await state.set_state(AdminFSM.waiting_uid)
    await callback.answer()


@router.message(AdminFSM.waiting_uid)
async def admin_get_uid(message: Message, state: FSMContext, lang: str):
    try:
        uid = int(message.text.strip())
        user = await get_user(uid)
        if not user:
            await message.answer("❌ Пользователь не найден!" if lang == "ru" else "❌ User not found!")
            await state.clear()
            return
        await state.update_data(uid=uid)
        await state.set_state(AdminFSM.waiting_amount)
        await message.answer(
            f"👤 {user['full_name']}\n"
            f"💰 {'Баланс' if lang == 'ru' else 'Balance'}: {format_ton(user['balance'])} TON\n\n"
            f"{'Введите сумму:' if lang == 'ru' else 'Enter amount:'}"
        )
    except ValueError:
        await message.answer("❌ Неверный ID" if lang == "ru" else "❌ Invalid ID")


@router.message(AdminFSM.waiting_amount)
async def admin_get_amount(message: Message, state: FSMContext, lang: str):
    try:
        amount = float(message.text.strip())
        data = await state.get_data()
        uid = data["uid"]
        await update_balance(uid, amount)
        user = await get_user(uid)
        await state.clear()
        await message.answer(
            f"✅ {'Начислено' if lang == 'ru' else 'Added'}: <b>{amount} TON</b>\n"
            f"👤 {user['full_name']}\n"
            f"💰 {'Новый баланс' if lang == 'ru' else 'New balance'}: <b>{format_ton(user['balance'])} TON</b>",
            parse_mode="HTML"
        )
    except ValueError:
        await message.answer("❌ Неверная сумма" if lang == "ru" else "❌ Invalid amount")


@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("No access", show_alert=True)
        return

    async with aiosqlite.connect("workers.db") as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cur:
            users = (await cur.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM workers") as cur:
            workers_count = (await cur.fetchone())[0]
        async with db.execute("SELECT COALESCE(SUM(total_earned), 0) FROM users") as cur:
            earned = (await cur.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM withdrawals WHERE status='pending'") as cur:
            pending = (await cur.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM withdrawals WHERE status='approved'") as cur:
            approved = (await cur.fetchone())[0]

    await callback.message.edit_text(
        "╔══════════════════════╗\n"
        "║  📊 СТАТИСТИКА БОТА  ║\n"
        "╚══════════════════════╝\n\n"
        f"👥 Пользователей: <b>{users}</b>\n"
        f"👷 Куплено рабочих: <b>{workers_count}</b>\n"
        f"💰 Всего заработано: <b>{earned:.2f} TON</b>\n\n"
        f"⏳ Заявок в ожидании: <b>{pending}</b>\n"
        f"✅ Одобрено выводов: <b>{approved}</b>",
        parse_mode="HTML"
    )
    await callback.answer()