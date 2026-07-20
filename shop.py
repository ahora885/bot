from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()


shop_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="5 گیگ",
                callback_data="volume_5"
            ),
            InlineKeyboardButton(
                text="10 گیگ",
                callback_data="volume_10"
            )
        ],
        [
            InlineKeyboardButton(
                text="20 گیگ",
                callback_data="volume_20"
            ),
            InlineKeyboardButton(
                text="50 گیگ",
                callback_data="volume_50"
            )
        ],
        [
            InlineKeyboardButton(
                text="100 گیگ",
                callback_data="volume_100"
            )
        ]
    ]
)


@router.message(lambda message: message.text == "📦 خرید کانفیگ")
async def shop_handler(message: types.Message):

    await message.answer(
        """
📦 خرید کانفیگ

حجم مورد نظر را انتخاب کنید:

💰 قیمت:
هر گیگ = ۲۰۰۰ تومان
هر روز = ۱۰۰۰ تومان
""",
        reply_markup=shop_menu
    )


@router.callback_query(lambda call: call.data.startswith("volume_"))
async def volume_select(call: types.CallbackQuery):

    volume = call.data.replace(
        "volume_",
        ""
    )

    await call.message.answer(
        f"""
✅ حجم انتخاب شد:
{volume} گیگ

حالا مدت زمان را انتخاب کنید.
"""
    )

    await call.answer()
