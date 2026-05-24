
import json
import os
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery


def load_locale(lang: str) -> dict:
    path = os.path.join("locales", f"{lang}.json")
    if not os.path.exists(path):
        path = os.path.join("locales", "ru.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


LOCALES = {
    "ru": load_locale("ru"),
    "en": load_locale("en"),
}


def t(key: str, lang: str = "ru", **kwargs) -> str:
    locale = LOCALES.get(lang, LOCALES["ru"])
    text = locale.get(key, LOCALES["ru"].get(key, key))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError):
            pass
    return text


class I18nMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        from database.db import get_user_language

        user = None
        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user

        lang = "ru"
        if user:
            try:
                lang = await get_user_language(user.id) or "ru"
            except Exception:
                lang = "ru"

        data["lang"] = lang
        data["t"] = lambda key, **kw: t(key, lang=lang, **kw)
        return await handler(event, data)