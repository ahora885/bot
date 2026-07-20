from aiogram import Router, types

router = Router()


@router.message(lambda message: message.text == "💰 کیف پول")
async def wallet_handler(message: types.Message):

    await message.answer(
        """
💰 کیف پول شما

💵 موجودی:
0 تومان

📜 تاریخچه تراکنش:
هنوز تراکنشی ندارید.
"""
    )