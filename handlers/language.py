from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from database.db import set_user_language
from keyboards.kb import language_keyboard, main_menu

router = Router()


@router.message(F.text == "🌍 Язык / Language")
async def choose_language(message: Message, lang: str):
    await message.answer(
        "🌍 <b>Выберите язык / Choose language:</b>",
        reply_markup=language_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "lang_ru")
async def set_ru(callback: CallbackQuery):
    await set_user_language(callback.from_user.id, "ru")
    await callback.message.edit_text("✅ <b>Язык изменён на Русский!</b>", parse_mode="HTML")
    await callback.message.answer("🏠 Главное меню", reply_markup=main_menu("ru"))
    await callback.answer()


@router.callback_query(F.data == "lang_en")
async def set_en(callback: CallbackQuery):
    await set_user_language(callback.from_user.id, "en")
    await callback.message.edit_text("✅ <b>Language changed to English!</b>", parse_mode="HTML")
    await callback.message.answer("🏠 Main Menu", reply_markup=main_menu("en"))
    await callback.answer()