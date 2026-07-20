from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import asyncio

from config import BOT_TOKEN, WELCOME_BONUS
from database import Session, User


bot = Bot(BOT_TOKEN)

dp = Dispatcher()


menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📦 خرید کانفیگ"),
            KeyboardButton(text="🆓 تست رایگان")
        ],
        [
            KeyboardButton(text="👤 اطلاعات حساب"),
            KeyboardButton(text="💰 کیف پول")
        ],
        [
            KeyboardButton(text="💬 پشتیبانی")
        ]
    ],
    resize_keyboard=True
)


@dp.message(Command("start"))
async def start(message: types.Message):

    db = Session()

    user = db.query(User).filter(
        User.telegram_id == message.from_user.id
    ).first()


    if not user:

        user = User(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            wallet=WELCOME_BONUS,
            welcome_bonus=True
        )

        db.add(user)
        db.commit()

        await message.answer(
            "🎉 خوش آمدید!\n\n"
            "💰 ۲۰ هزار تومان هدیه ورود به کیف پول شما اضافه شد.",
            reply_markup=menu
        )

    else:

        await message.answer(
            "👋 خوش آمدید دوباره",
            reply_markup=menu
        )


    db.close()



@dp.message(lambda m: m.text=="👤 اطلاعات حساب")
async def account(message:types.Message):

    db=Session()

    user=db.query(User).filter(
        User.telegram_id==message.from_user.id
    ).first()


    await message.answer(
        f"""
👤 اطلاعات حساب

🆔 آیدی:
{user.telegram_id}

👤 اسم:
{user.first_name}

📛 یوزرنیم:
@{user.username if user.username else 'ندارد'}

💰 کیف پول:
{user.wallet} تومان

🆓 تست باقی مانده:
{3-user.free_test_count}

📦 کانفیگ خریداری شده:
{user.configs}
"""
    )

    db.close()



@dp.message(lambda m:m.text=="💰 کیف پول")
async def wallet(message:types.Message):

    db=Session()

    user=db.query(User).filter(
        User.telegram_id==message.from_user.id
    ).first()


    await message.answer(
        f"""
💰 کیف پول

موجودی:
{user.wallet} تومان
"""
    )

    db.close()



async def main():

    await dp.start_polling(bot)



if __name__=="__main__":
    asyncio.run(main())