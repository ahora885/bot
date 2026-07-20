from aiogram import Router, types

router = Router()


@router.message(lambda message: message.text == "📦 خرید کانفیگ")
async def shop_handler(message: types.Message):

    await message.answer(
        """
📦 خرید کانفیگ

لطفاً حجم و مدت زمان کانفیگ را انتخاب کنید.

حجم‌ها:
5GB
10GB
20GB
50GB
100GB

مدت:
7 روز تا 3 ماه

💰 قیمت:
هر گیگ = 2000 تومان
هر روز = 1000 تومان
"""
    )