from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

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

    await message.answer(
        "🎉 خوش آمدید به ربات VPN\n\n"
        "از منوی زیر انتخاب کنید:",
        reply_markup=main_menu
    )