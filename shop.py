from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from sqlalchemy import select

from database import AsyncSessionLocal, User, Order


router = Router()


user_selected_volume = {}


volume_menu = InlineKeyboardMarkup(
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


days_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="7 روز",
                callback_data="days_7"
            ),
            InlineKeyboardButton(
                text="15 روز",
                callback_data="days_15"
            )
        ],
        [
            InlineKeyboardButton(
                text="30 روز",
                callback_data="days_30"
            ),
            InlineKeyboardButton(
                text="90 روز",
                callback_data="days_90"
            )
        ]
    ]
)



@router.message(lambda message: message.text == "📦 خرید کانفیگ")
async def shop_start(message: types.Message):

    await message.answer(
        """
📦 خرید کانفیگ

حجم مورد نظر را انتخاب کنید:

💰 هر گیگ: ۲۰۰۰ تومان
➕ هر روز: ۱۰۰۰ تومان
""",
        reply_markup=volume_menu
    )



@router.callback_query(lambda call: call.data.startswith("volume_"))
async def select_volume(call: CallbackQuery):

    volume = int(
        call.data.replace(
            "volume_",
            ""
        )
    )


    user_selected_volume[call.from_user.id] = volume


    await call.message.answer(
        "⏳ مدت زمان را انتخاب کنید:",
        reply_markup=days_menu
    )


    await call.answer()



@router.callback_query(lambda call: call.data.startswith("days_"))
async def select_days(call: CallbackQuery):

    days = int(
        call.data.replace(
            "days_",
            ""
        )
    )


    volume = user_selected_volume.get(
        call.from_user.id
    )


    if not volume:

        await call.message.answer(
            "❌ دوباره خرید را شروع کنید."
        )

        return


    price = (
        volume * 2000
    ) + (
        days * 1000
    )


    buy_button = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ خرید",
                    callback_data=f"buy_{volume}_{days}"
                )
            ]
        ]
    )


    await call.message.answer(
        f"""
🧾 فاکتور خرید

📦 حجم:
{volume} گیگ

⏳ مدت:
{days} روز

💰 قیمت:
{price} تومان
""",
        reply_markup=buy_button
    )


    await call.answer()



@router.callback_query(lambda call: call.data.startswith("buy_"))
async def buy_config(call: CallbackQuery):

    data = call.data.split("_")

    volume = int(data[1])
    days = int(data[2])


    price = (
        volume * 2000
    ) + (
        days * 1000
    )


    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(User).where(
                User.telegram_id == call.from_user.id
            )
        )

        user = result.scalar_one_or_none()


        if not user:

            await call.message.answer(
                "❌ اول /start را بزنید."
            )

            return


        if user.wallet < price:

            await call.message.answer(
                f"""
❌ موجودی کافی نیست.

💰 موجودی:
{user.wallet}

🧾 قیمت:
{price}
"""
            )

            return


        user.wallet -= price
        user.configs += 1


        order = Order(
            telegram_id=call.from_user.id,
            volume=volume,
            days=days,
            price=price,
            status="paid"
        )


        session.add(order)

        await session.commit()



    await call.message.answer(
        """
✅ خرید با موفقیت انجام شد.

⏳ کانفیگ شما بعداً ارسال می‌شود.
"""
    )


    await call.answer()
