from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from database.db import (get_user, update_balance, create_withdrawal,
                          get_withdrawal, update_withdrawal_status, get_withdrawn_today)
from keyboards.kb import (withdraw_speed_keyboard, withdraw_wallet_keyboard,
                           withdraw_confirm_keyboard, admin_withdraw_keyboard)
from utils.helpers import format_ton
from config import (WITHDRAW_MIN, WITHDRAW_FEE_NORMAL, WITHDRAW_FEE_FAST,
                    WITHDRAW_FEE_INSTANT, WITHDRAW_MAX_DAY, LOG_CHAT_ID, SUPPORT_USERNAME)

router = Router()

FEES = {
    "normal": WITHDRAW_FEE_NORMAL,
    "fast": WITHDRAW_FEE_FAST,
    "instant": WITHDRAW_FEE_INSTANT,
}


class WithdrawFSM(StatesGroup):
    waiting_amount = State()
    waiting_address = State()


@router.message(F.text.in_(["💸 Вывод", "💸 Withdraw"]))
async def start_withdraw(message: Message, state: FSMContext, lang: str):
    user = await get_user(message.from_user.id)
    today_withdrawn = await get_withdrawn_today(message.from_user.id)
    available_today = WITHDRAW_MAX_DAY - today_withdrawn

    if lang == "ru":
        text = (
            "╔══════════════════════╗\n"
            "║    💸 ВЫВОД СРЕДСТВ  ║\n"
            "╚══════════════════════╝\n\n"
            f"💰 Баланс: <b>{format_ton(user['balance'])} TON</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📋 Минимум: <b>{WITHDRAW_MIN} TON</b>\n"
            f"📋 Максимум сегодня: <b>{format_ton(available_today)} TON</b>\n"
            f"📋 Лимит в месяц: <b>5000 TON</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "✏️ <b>Введите сумму для вывода:</b>"
        )
    else:
        text = (
            "╔══════════════════════╗\n"
            "║    💸 WITHDRAW       ║\n"
            "╚══════════════════════╝\n\n"
            f"💰 Balance: <b>{format_ton(user['balance'])} TON</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📋 Minimum: <b>{WITHDRAW_MIN} TON</b>\n"
            f"📋 Available today: <b>{format_ton(available_today)} TON</b>\n"
            f"📋 Monthly limit: <b>5000 TON</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "✏️ <b>Enter withdrawal amount:</b>"
        )

    await message.answer(text, parse_mode="HTML")
    await state.set_state(WithdrawFSM.waiting_amount)
    await state.update_data(lang=lang)


@router.message(WithdrawFSM.waiting_amount)
async def process_amount(message: Message, state: FSMContext, lang: str):
    try:
        amount = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer(
            "❌ Введите корректную сумму!" if lang == "ru" else "❌ Enter a valid amount!"
        )
        return

    user_id = message.from_user.id
    user = await get_user(user_id)
    today_withdrawn = await get_withdrawn_today(user_id)
    available_today = WITHDRAW_MAX_DAY - today_withdrawn

    if amount < WITHDRAW_MIN:
        await message.answer(
            f"❌ {'Минимум' if lang == 'ru' else 'Minimum'}: <b>{WITHDRAW_MIN} TON</b>",
            parse_mode="HTML"
        )
        return
    if amount > available_today:
        await message.answer(
            f"❌ {'Доступно сегодня' if lang == 'ru' else 'Available today'}: "
            f"<b>{format_ton(available_today)} TON</b>",
            parse_mode="HTML"
        )
        return
    if amount > user["balance"]:
        await message.answer(
            f"❌ {'Недостаточно средств!' if lang == 'ru' else 'Not enough funds!'}\n"
            f"{'Доступно' if lang == 'ru' else 'Available'}: <b>{format_ton(user['balance'])} TON</b>",
            parse_mode="HTML"
        )
        return

    await state.update_data(amount=amount)
    await message.answer(
        f"💸 {'Вывод' if lang == 'ru' else 'Withdraw'}: <b>{format_ton(amount)} TON</b>\n\n"
        f"{'Выберите скорость:' if lang == 'ru' else 'Choose speed:'}",
        reply_markup=withdraw_speed_keyboard(amount, lang),
        parse_mode="HTML"
    )
    await state.clear()


@router.callback_query(F.data.startswith("wspeed_"))
async def choose_speed(callback: CallbackQuery, state: FSMContext, lang: str):
    parts = callback.data.split("_")
    speed = parts[1]
    amount = float(parts[2])

    fee_rate = FEES.get(speed, WITHDRAW_FEE_NORMAL)
    fee = round(amount * fee_rate, 4)
    final = round(amount - fee, 4)

    await state.update_data(speed=speed, amount=amount, fee=fee, final=final)
    await callback.message.edit_text(
        f"💸 {'Выберите кошелёк:' if lang == 'ru' else 'Choose wallet:'}\n\n"
        f"💰 {'Сумма' if lang == 'ru' else 'Amount'}: <b>{format_ton(amount)} TON</b>\n"
        f"💸 {'Комиссия' if lang == 'ru' else 'Fee'}: <b>{format_ton(fee)} TON</b>\n"
        f"📤 {'К выплате' if lang == 'ru' else 'To receive'}: <b>{format_ton(final)} TON</b>",
        reply_markup=withdraw_wallet_keyboard(amount, speed, lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("wwallet_"))
async def choose_wallet(callback: CallbackQuery, state: FSMContext, lang: str):
    parts = callback.data.split("_")
    wallet_type = parts[1]
    speed = parts[2]
    amount = float(parts[3])

    await state.update_data(wallet_type=wallet_type, speed=speed, amount=amount)
    await state.set_state(WithdrawFSM.waiting_address)

    await callback.message.edit_text(
        f"📝 {'Введите адрес' if lang == 'ru' else 'Enter address'} "
        f"<b>{wallet_type}</b> {'кошелька:' if lang == 'ru' else 'wallet:'}",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(WithdrawFSM.waiting_address)
async def process_address(message: Message, state: FSMContext, lang: str, bot: Bot):
    data = await state.get_data()
    address = message.text.strip()
    amount = data["amount"]
    speed = data["speed"]
    wallet_type = data["wallet_type"]

    fee_rate = FEES.get(speed, WITHDRAW_FEE_NORMAL)
    fee = round(amount * fee_rate, 4)
    final = round(amount - fee, 4)

    speed_labels = {
        "ru": {"normal": "🐢 Обычный", "fast": "🚀 Быстрый", "instant": "⚡ Мгновенный"},
        "en": {"normal": "🐢 Normal", "fast": "🚀 Fast", "instant": "⚡ Instant"},
    }
    speed_label = speed_labels.get(lang, speed_labels["ru"]).get(speed, speed)

    withdraw_id = await create_withdrawal(
        message.from_user.id, amount, final, fee, speed, wallet_type, address
    )
    await update_balance(message.from_user.id, -amount)
    await state.clear()

    if lang == "ru":
        text = (
            "╔══════════════════════╗\n"
            "║  ✅ ПОДТВЕРЖДЕНИЕ    ║\n"
            "╚══════════════════════╝\n\n"
            f"💰 Сумма: <b>{format_ton(amount)} TON</b>\n"
            f"💸 Комиссия: <b>{format_ton(fee)} TON ({int(fee_rate*100)}%)</b>\n"
            f"📤 К выплате: <b>{format_ton(final)} TON</b>\n"
            f"🚀 Скорость: <b>{speed_label}</b>\n"
            f"💳 Кошелёк: <b>{wallet_type}</b>\n"
            f"📍 Адрес: <code>{address}</code>"
        )
    else:
        text = (
            "╔══════════════════════╗\n"
            "║  ✅ CONFIRMATION     ║\n"
            "╚══════════════════════╝\n\n"
            f"💰 Amount: <b>{format_ton(amount)} TON</b>\n"
            f"💸 Fee: <b>{format_ton(fee)} TON ({int(fee_rate*100)}%)</b>\n"
            f"📤 To receive: <b>{format_ton(final)} TON</b>\n"
            f"🚀 Speed: <b>{speed_label}</b>\n"
            f"💳 Wallet: <b>{wallet_type}</b>\n"
            f"📍 Address: <code>{address}</code>"
        )

    await message.answer(
        text,
        reply_markup=withdraw_confirm_keyboard(withdraw_id, lang),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("wconfirm_"))
async def confirm_withdraw(callback: CallbackQuery, lang: str, bot: Bot):
    withdraw_id = int(callback.data.split("_")[1])
    w = await get_withdrawal(withdraw_id)
    if not w:
        await callback.answer("Error", show_alert=True)
        return

    from database.db import get_user
    user = await get_user(w["user_id"])
    speed_labels = {
        "ru": {"normal": "🐢 Обычный", "fast": "🚀 Быстрый", "instant": "⚡ Мгновенный"},
        "en": {"normal": "🐢 Normal", "fast": "🚀 Fast", "instant": "⚡ Instant"},
    }
    speed_label = speed_labels.get(lang, speed_labels["ru"]).get(w["speed"], w["speed"])

    await callback.message.edit_text(
        f"✅ <b>{'Заявка отправлена!' if lang == 'ru' else 'Request sent!'}</b>\n\n"
        f"💰 {'Сумма' if lang == 'ru' else 'Amount'}: <b>{format_ton(w['amount'])} TON</b>\n"
        f"📤 {'К выплате' if lang == 'ru' else 'To receive'}: <b>{format_ton(w['final_amount'])} TON</b>\n"
        f"⏰ {'Ожидайте подтверждения' if lang == 'ru' else 'Awaiting confirmation'}",
        parse_mode="HTML"
    )

    try:
        await bot.send_message(
            LOG_CHAT_ID,
            f"💸 <b>Новая заявка на вывод!</b>\n\n"
            f"👤 {user['full_name']} (ID: <code>{user['user_id']}</code>)\n"
            f"💰 Сумма: <b>{format_ton(w['amount'])} TON</b>\n"
            f"📤 К выплате: <b>{format_ton(w['final_amount'])} TON</b>\n"
            f"💳 {w['wallet_type']}: <code>{w['address']}</code>\n"
            f"🚀 {speed_label}",
            reply_markup=admin_withdraw_keyboard(withdraw_id),
            parse_mode="HTML"
        )
    except Exception:
        pass

    await callback.answer()