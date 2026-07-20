import asyncio

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from database import create_tables

from handlers import start
from handlers import account
from handlers import wallet
from handlers import shop
from handlers import support
from handlers import admin



async def main():

    await create_tables()


    bot = Bot(
        token=BOT_TOKEN
    )

    dp = Dispatcher()


    dp.include_router(
        start.router
    )

    dp.include_router(
        account.router
    )

    dp.include_router(
        wallet.router
    )

    dp.include_router(
        shop.router
    )

    dp.include_router(
        support.router
    )

    dp.include_router(
        admin.router
    )


    await dp.start_polling(
        bot
    )



if __name__ == "__main__":

    asyncio.run(
        main()
    )
