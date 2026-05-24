from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from database.db import get_user, update_balance, add_worker
from keyboards.kb import shop_keyboard, confirm_buy_keyboard
from middlewares.i18n import t
from utils.helpers import calculate_income, format_ton, get_worker_name, check_achievements
from config import WORKERS, ACHIEVEMENTS

router = Router()


@router.message(F.text.in_(["🏪 Магазин", "🏪 Shop"]))
async def show_shop(message: Message, lang: str):
    user = await get_user(message.from_user.id)
    income = await calculate_income(message.from_user.id)

    text = (
        "╔══════════════════════╗\n"
        f"║    {'🏪 МАГАЗИН' if lang == 'ru' else '🏪 SHOP'}         ║\n"
        "╚══════════════════════╝\n\n"
        f"💰 {t('balance', lang)}: <b>{format_ton(user['balance'])} TON</b>\n"
        f"📈 {t('income_day', lang)}: <b>{format_ton(income)} TON</b>\n\n"
        f"{'👇 Выберите рабочего:' if lang == 'ru' else '👇 Choose a worker:'}"
    )
    await message.answer(text, reply_markup=shop_keyboard(lang), parse_mode="HTML")


@router.callback_query(F.data == "back_shop")
async def back_shop(callback: CallbackQuery, lang: str):
    user = await get_user(callback.from_user.id)
    income = await calculate_income(callback.from_user.id)

    text = (
        "╔══════════════════════╗\n"
        f"║    {'🏪 МАГАЗИН' if lang == 'ru' else '🏪 SHOP'}         ║\n"
        "╚══════════════════════╝\n\n"
        f"💰 {t('balance', lang)}: <b>{format_ton(user['balance'])} TON</b>\n"
        f"📈 {t('income_day', lang)}: <b>{format_ton(income)} TON</b>\n\n"
        f"{'👇 Выберите рабочего:' if lang == 'ru' else '👇 Choose a worker:'}"
    )
    await callback.message.edit_text(text, reply_markup=shop_keyboard(lang), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("buy_worker_"))
async def buy_worker_info(callback: CallbackQuery, lang: str):
    worker_id = int(callback.data.split("_")[2])
    wdata = WORKERS[worker_id]
    name = get_worker_name(worker_id, lang)

    income_hour = wdata["income_day"] / 24
    income_week = wdata["income_day"] * 7

    text = (
        f"╔══════════════════════╗\n"
        f"║  {name[:20]:<20}  ║\n"
        f"╚══════════════════════╝\n\n"
        f"💵 {'Стоимость' if lang == 'ru' else 'Cost'}: <b>{wdata['cost']} TON</b>\n\n"
        f"📊 {'Доход:' if lang == 'ru' else 'Income:'}\n"
        f"  ⏰ {'В час' if lang == 'ru' else 'Per hour'}: <b>{income_hour:.4f} TON</b>\n"
        f"  📅 {'В день' if lang == 'ru' else 'Per day'}: <b>{wdata['income_day']} TON</b>\n"
        f"  📆 {'В неделю' if lang == 'ru' else 'Per week'}: <b>{income_week:.3f} TON</b>\n\n"
        f"{'💡 Окупаемость' if lang == 'ru' else '💡 Payback'}: "
        f"<b>{wdata['cost'] / wdata['income_day']:.1f} {'дней' if lang == 'ru' else 'days'}</b>"
    )
    await callback.message.edit_text(
        text,
        reply_markup=confirm_buy_keyboard(worker_id, lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_buy_"))
async def confirm_buy(callback: CallbackQuery, lang: str):
    worker_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id
    wdata = WORKERS[worker_id]
    user = await get_user(user_id)
    name = get_worker_name(worker_id, lang)

    if user["balance"] < wdata["cost"]:
        await callback.answer(
            f"❌ {'Недостаточно средств!' if lang == 'ru' else 'Not enough funds!'}\n"
            f"{'Нужно' if lang == 'ru' else 'Need'}: {wdata['cost']} TON\n"
            f"{'Баланс' if lang == 'ru' else 'Balance'}: {format_ton(user['balance'])} TON",
            show_alert=True
        )
        return

    await update_balance(user_id, -wdata["cost"])
    await add_worker(user_id, worker_id)
    income = await calculate_income(user_id)
    user = await get_user(user_id)
    new_achs = await check_achievements(user_id)

    text = (
        f"🎉 <b>{'Покупка успешна!' if lang == 'ru' else 'Purchase successful!'}</b>\n\n"
        f"{'Куплен' if lang == 'ru' else 'Bought'}: <b>{name}</b>\n"
        f"💸 {'Списано' if lang == 'ru' else 'Spent'}: <b>{wdata['cost']} TON</b>\n"
        f"💰 {'Баланс' if lang == 'ru' else 'Balance'}: <b>{format_ton(user['balance'])} TON</b>\n"
        f"📈 {'Новый доход/день' if lang == 'ru' else 'New income/day'}: <b>{format_ton(income)} TON</b>"
    )
    await callback.message.edit_text(text, parse_mode="HTML")

    if new_achs:
        for ach in new_achs:
            ach_data = ACHIEVEMENTS[ach]
            ach_name = ach_data.get(f"name_{lang}", ach_data["name_ru"])
            ach_title = ach_data.get(f"title_{lang}", ach_data["title_ru"])
            await callback.message.answer(
                f"🏅 <b>{'Новое достижение!' if lang == 'ru' else 'New Achievement!'}</b>\n\n"
                f"🎖 {ach_name}\n"
                f"👑 {'Титул' if lang == 'ru' else 'Title'}: <b>{ach_title}</b>\n"
                f"💰 {'Награда' if lang == 'ru' else 'Reward'}: <b>+{ach_data['reward']} TON</b>",
                parse_mode="HTML"
            )
    await callback.answer()