from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from middlewares.i18n import t
from config import WORKERS, TEMP_BOOSTS, PERM_BOOSTS


def main_menu(lang: str = "ru") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("btn_shop", lang)), KeyboardButton(text=t("btn_workers", lang))],
            [KeyboardButton(text=t("btn_farm", lang)), KeyboardButton(text=t("btn_boosts", lang))],
            [KeyboardButton(text=t("btn_daily", lang)), KeyboardButton(text=t("btn_referral", lang))],
            [KeyboardButton(text=t("btn_withdraw", lang)), KeyboardButton(text=t("btn_stats", lang))],
            [KeyboardButton(text=t("btn_language", lang))],
        ],
        resize_keyboard=True
    )


def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
        ]
    ])


def shop_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    buttons = []
    for wid, wdata in WORKERS.items():
        name = wdata.get(f"name_{lang}", wdata["name_ru"])
        buttons.append([InlineKeyboardButton(
            text=f"{name} — {wdata['cost']} TON",
            callback_data=f"buy_worker_{wid}"
        )])
    buttons.append([InlineKeyboardButton(text=t("btn_back", lang), callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def confirm_buy_keyboard(worker_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t("btn_confirm", lang), callback_data=f"confirm_buy_{worker_id}"),
            InlineKeyboardButton(text=t("btn_cancel", lang), callback_data="back_shop"),
        ]
    ])


def workers_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("btn_collect", lang), callback_data="collect_income")],
        [InlineKeyboardButton(text=t("btn_back", lang), callback_data="back_main")],
    ])


def farm_keyboard(can_upgrade: bool, cost: float, is_max: bool, lang: str = "ru") -> InlineKeyboardMarkup:
    buttons = []
    if not is_max and can_upgrade:
        buttons.append([InlineKeyboardButton(
            text=t("btn_upgrade_farm", lang, cost=cost),
            callback_data="upgrade_farm"
        )])
    buttons.append([InlineKeyboardButton(text=t("btn_back", lang), callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def boosts_menu_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("btn_temp_boosts", lang), callback_data="show_temp_boosts")],
        [InlineKeyboardButton(text=t("btn_perm_boosts", lang), callback_data="show_perm_boosts")],
        [InlineKeyboardButton(text=t("btn_back", lang), callback_data="back_main")],
    ])


def temp_boosts_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    buttons = []
    for key, data in TEMP_BOOSTS.items():
        name = data.get(f"name_{lang}", data["name_ru"])
        buttons.append([InlineKeyboardButton(
            text=f"{name} — {data['cost']} TON (+{int((data['multiplier']-1)*100)}%)",
            callback_data=f"buy_temp_{key}"
        )])
    buttons.append([InlineKeyboardButton(text=t("btn_back", lang), callback_data="show_boosts")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def perm_boosts_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    buttons = []
    for key, data in PERM_BOOSTS.items():
        name = data.get(f"name_{lang}", data["name_ru"])
        buttons.append([InlineKeyboardButton(
            text=f"{name} — {data['cost']} TON (+{int(data['bonus']*100)}%)",
            callback_data=f"buy_perm_{key}"
        )])
    buttons.append([InlineKeyboardButton(text=t("btn_back", lang), callback_data="show_boosts")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def withdraw_speed_keyboard(amount: float, lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("speed_normal", lang), callback_data=f"wspeed_normal_{amount}")],
        [InlineKeyboardButton(text=t("speed_fast", lang), callback_data=f"wspeed_fast_{amount}")],
        [InlineKeyboardButton(text=t("speed_instant", lang), callback_data=f"wspeed_instant_{amount}")],
        [InlineKeyboardButton(text=t("btn_cancel", lang), callback_data="back_main")],
    ])


def withdraw_wallet_keyboard(amount: float, speed: str, lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 TON", callback_data=f"wwallet_TON_{speed}_{amount}")],
        [InlineKeyboardButton(text="💵 USDT", callback_data=f"wwallet_USDT_{speed}_{amount}")],
        [InlineKeyboardButton(text=t("btn_cancel", lang), callback_data="back_main")],
    ])


def withdraw_confirm_keyboard(withdraw_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t("btn_confirm", lang), callback_data=f"wconfirm_{withdraw_id}"),
            InlineKeyboardButton(text=t("btn_cancel", lang), callback_data="back_main"),
        ]
    ])


def admin_withdraw_keyboard(withdraw_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Одобрить", callback_data=f"admin_approve_{withdraw_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"admin_reject_{withdraw_id}"),
        ]
    ])


def stats_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("btn_top", lang), callback_data="show_top")],
        [InlineKeyboardButton(text=t("btn_achievements", lang), callback_data="show_achievements")],
        [InlineKeyboardButton(text=t("btn_back", lang), callback_data="back_main")],
    ])


def admin_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("btn_admin_withdraws", lang), callback_data="admin_withdraws")],
        [InlineKeyboardButton(text=t("btn_admin_balance", lang), callback_data="admin_add_balance")],
        [InlineKeyboardButton(text=t("btn_admin_stats", lang), callback_data="admin_stats")],
    ])