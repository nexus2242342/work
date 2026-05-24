import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from database.db import init_db
from middlewares.i18n import I18nMiddleware
from handlers import start, shop, workers, farm, boosts, daily, referral, withdraw, stats, admin, language

logging.basicConfig(level=logging.INFO)


async def main():
    await init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.message.middleware(I18nMiddleware())
    dp.callback_query.middleware(I18nMiddleware())

    dp.include_router(language.router)
    dp.include_router(start.router)
    dp.include_router(shop.router)
    dp.include_router(workers.router)
    dp.include_router(farm.router)
    dp.include_router(boosts.router)
    dp.include_router(daily.router)
    dp.include_router(referral.router)
    dp.include_router(withdraw.router)
    dp.include_router(stats.router)
    dp.include_router(admin.router)

    print("✅ Bot started!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())