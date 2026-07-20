from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from database import Session, User
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
            "💰 مبلغ ۲۰ هزار تومان هدیه ورود به کیف پول شما اضافه شد.",
            reply_markup=main_menu
        )


    else:

        await message.answer(
            "👋 خوش آمدید دوباره!",
            reply_markup=main_menu
        )


    db.close()
