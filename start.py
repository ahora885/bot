from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from sqlalchemy import select

from database import AsyncSessionLocal, User
from config import WELCOME_BONUS


router = Router()


main_menu = ReplyKeyboardMarkup(
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


@router.message(Command("start"))
async def start_handler(message: types.Message):

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(User).where(
                User.telegram_id == message.from_user.id
            )
        )

        user = result.scalar_one_or_none()


        if not user:

            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                wallet=WELCOME_BONUS,
                welcome_bonus=True
            )

            session.add(user)

            await session.commit()


            await message.answer(
                "🎉 خوش آمدید!\n\n"
                "💰 مبلغ ۲۰ هزار تومان هدیه ورود به کیف پول شما اضافه شد.",
                reply_markup=main_menu
            )

        else:

            await message.answer(
                "👋 خوش آمدید دوباره!",
                reply_markup=main_menu
            )
