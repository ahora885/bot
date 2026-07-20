import asyncio

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN

from start import router as start_router
from account import router as account_router
from wallet import router as wallet_router
from shop import router as shop_router
from support import router as support_router
from admin import router as admin_router


bot = Bot(BOT_TOKEN)

dp = Dispatcher()


dp.include_router(start_router)
dp.include_router(account_router)
dp.include_router(wallet_router)
dp.include_router(shop_router)
dp.include_router(support_router)
dp.include_router(admin_router)


async def main():
    print("Bot Started...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
