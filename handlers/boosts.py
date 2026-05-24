from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from database.db import (get_user, update_balance, add_temp_boost,
                          add_perm_boost, get_active_boosts, get_perm_boosts)
from keyboards.kb import boosts_menu_keyboard, temp_boosts_keyboard, perm_boosts_keyboard
from utils.helpers import format_ton, get_boost_name
from config import TEMP_BOOSTS, PERM_BOOSTS

router = Router()


@router.message(F.text.in_(["⚡ Бусты", "⚡ Boosts"]))
async def show_boosts(message: Message, lang: str):
    user = await get_user(message.from_user.id)
    active = await get_active_boosts(message.from_user.id)
    owned = await get_perm_boosts(message.from_user.id)

    if lang == "ru":
        text = (
            "╔══════════════════════╗\n"
            "║       ⚡ БУСТЫ       ║\n"
            "╚══════════════════════╝\n\n"
            f"💰 Баланс: <b>{format_ton(user['balance'])} TON</b>\n\n"
            f"⚡ Активных бустов: <b>{len(active)}</b>\n"
            f"♾️ Постоянных бустов: <b>{len(owned)}</b>"
        )
    else:
        text = (
            "╔══════════════════════╗\n"
            "║       ⚡ BOOSTS      ║\n"
            "╚══════════════════════╝\n\n"
            f"💰 Balance: <b>{format_ton(user['balance'])} TON</b>\n\n"
            f"⚡ Active boosts: <b>{len(active)}</b>\n"
            f"♾️ Permanent boosts: <b>{len(owned)}</b>"
        )

    await message.answer(text, reply_markup=boosts_menu_keyboard(lang), parse_mode="HTML")


@router.callback_query(F.data == "show_boosts")
async def show_boosts_cb(callback: CallbackQuery, lang: str):
    user = await get_user(callback.from_user.id)
    active = await get_active_boosts(callback.from_user.id)
    owned = await get_perm_boosts(callback.from_user.id)

    if lang == "ru":
        text = (
            "╔══════════════════════╗\n"
            "║       ⚡ БУСТЫ       ║\n"
            "╚══════════════════════╝\n\n"
            f"💰 Баланс: <b>{format_ton(user['balance'])} TON</b>\n\n"
            f"⚡ Активных бустов: <b>{len(active)}</b>\n"
            f"♾️ Постоянных бустов: <b>{len(owned)}</b>"
        )
    else:
        text = (
            "╔══════════════════════╗\n"
            "║       ⚡ BOOSTS      ║\n"
            "╚══════════════════════╝\n\n"
            f"💰 Balance: <b>{format_ton(user['balance'])} TON</b>\n\n"
            f"⚡ Active boosts: <b>{len(active)}</b>\n"
            f"♾️ Permanent boosts: <b>{len(owned)}</b>"
        )
    await callback.message.edit_text(text, reply_markup=boosts_menu_keyboard(lang), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "show_temp_boosts")
async def show_temp(callback: CallbackQuery, lang: str):
    user = await get_user(callback.from_user.id)
    active = await get_active_boosts(callback.from_user.id)
    active_keys = {b["boost_key"]: b for b in active}

    if lang == "ru":
        text = (
            "╔══════════════════════╗\n"
            "║  ⚡ ВРЕМЕННЫЕ БУСТЫ  ║\n"
            "╚══════════════════════╝\n\n"
            f"💰 Баланс: <b>{format_ton(user['balance'])} TON</b>\n\n"
        )
    else:
        text = (
            "╔══════════════════════╗\n"
            "║  ⚡ TEMPORARY BOOSTS ║\n"
            "╚══════════════════════╝\n\n"
            f"💰 Balance: <b>{format_ton(user['balance'])} TON</b>\n\n"
        )

    for key, data in TEMP_BOOSTS.items():
        name = get_boost_name(key, TEMP_BOOSTS, lang)
        if key in active_keys:
            exp = active_keys[key]["expires_at"]
            status = f"✅ {'Активен до' if lang == 'ru' else 'Active until'}: {str(exp)[:16]}"
        else:
            status = f"💰 {data['cost']} TON"
        text += (
            f"<b>{name}</b>\n"
            f"  📈 +{int((data['multiplier']-1)*100)}% | "
            f"⏰ {data['hours']}h | {status}\n\n"
        )

    await callback.message.edit_text(
        text, reply_markup=temp_boosts_keyboard(lang), parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "show_perm_boosts")
async def show_perm(callback: CallbackQuery, lang: str):
    user = await get_user(callback.from_user.id)
    owned = await get_perm_boosts(callback.from_user.id)

    if lang == "ru":
        text = (
            "╔══════════════════════╗\n"
            "║ ♾️ ПОСТОЯННЫЕ БУСТЫ  ║\n"
            "╚══════════════════════╝\n\n"
            f"💰 Баланс: <b>{format_ton(user['balance'])} TON</b>\n\n"
        )
    else:
        text = (
            "╔══════════════════════╗\n"
            "║  ♾️ PERMANENT BOOSTS ║\n"
            "╚══════════════════════╝\n\n"
            f"💰 Balance: <b>{format_ton(user['balance'])} TON</b>\n\n"
        )

    for key, data in PERM_BOOSTS.items():
        name = get_boost_name(key, PERM_BOOSTS, lang)
        status = f"✅ {'Куплен' if lang == 'ru' else 'Owned'}" if key in owned else f"💰 {data['cost']} TON"
        text += (
            f"<b>{name}</b>\n"
            f"  📈 +{int(data['bonus']*100)}% | {status}\n\n"
        )

    await callback.message.edit_text(
        text, reply_markup=perm_boosts_keyboard(lang), parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("buy_temp_"))
async def buy_temp_boost(callback: CallbackQuery, lang: str):
    boost_key = callback.data.replace("buy_temp_", "")
    boost = TEMP_BOOSTS.get(boost_key)
    if not boost:
        await callback.answer("Error", show_alert=True)
        return

    user_id = callback.from_user.id
    user = await get_user(user_id)
    name = get_boost_name(boost_key, TEMP_BOOSTS, lang)

    if user["balance"] < boost["cost"]:
        await callback.answer(
            f"❌ {'Недостаточно средств!' if lang == 'ru' else 'Not enough funds!'}\n"
            f"{'Нужно' if lang == 'ru' else 'Need'}: {boost['cost']} TON",
            show_alert=True
        )
        return

    result = await add_temp_boost(user_id, boost_key, boost["multiplier"], boost["hours"])
    if not result:
        await callback.answer(
            "⚠️ У вас уже активен этот буст!" if lang == "ru" else "⚠️ This boost is already active!",
            show_alert=True
        )
        return

    await update_balance(user_id, -boost["cost"])
    until = (datetime.now() + timedelta(hours=boost["hours"])).strftime("%d.%m.%Y %H:%M")

    await callback.message.edit_text(
        f"✅ <b>{'Буст активирован!' if lang == 'ru' else 'Boost activated!'}</b>\n\n"
        f"⚡ {name}\n"
        f"📈 +{int((boost['multiplier']-1)*100)}%\n"
        f"⏰ {'До' if lang == 'ru' else 'Until'}: <b>{until}</b>\n"
        f"💰 {'Списано' if lang == 'ru' else 'Spent'}: <b>{boost['cost']} TON</b>",
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("buy_perm_"))
async def buy_perm_boost(callback: CallbackQuery, lang: str):
    boost_key = callback.data.replace("buy_perm_", "")
    boost = PERM_BOOSTS.get(boost_key)
    if not boost:
        await callback.answer("Error", show_alert=True)
        return

    user_id = callback.from_user.id
    user = await get_user(user_id)
    name = get_boost_name(boost_key, PERM_BOOSTS, lang)

    if user["balance"] < boost["cost"]:
        await callback.answer(
            f"❌ {'Недостаточно средств!' if lang == 'ru' else 'Not enough funds!'}\n"
            f"{'Нужно' if lang == 'ru' else 'Need'}: {boost['cost']} TON",
            show_alert=True
        )
        return

    result = await add_perm_boost(user_id, boost_key)
    if not result:
        await callback.answer(
            "⚠️ Вы уже купили этот буст!" if lang == "ru" else "⚠️ You already own this boost!",
            show_alert=True
        )
        return

    await update_balance(user_id, -boost["cost"])
    await callback.message.edit_text(
        f"✅ <b>{'Постоянный буст куплен!' if lang == 'ru' else 'Permanent boost purchased!'}</b>\n\n"
        f"📚 {name}\n"
        f"📈 +{int(boost['bonus']*100)}%\n"
        f"♾️ {'Навсегда!' if lang == 'ru' else 'Forever!'}\n"
        f"💰 {'Списано' if lang == 'ru' else 'Spent'}: <b>{boost['cost']} TON</b>",
        parse_mode="HTML"
    )
    await callback.answer()