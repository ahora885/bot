from aiogram import Router, types

router = Router()


@router.message(lambda message: message.text == "💬 پشتیبانی")
async def support_handler(message: types.Message):

    await message.answer(
        """
💬 پشتیبانی

پیام خود را ارسال کنید.
تیم پشتیبانی در اسرع وقت پاسخ می‌دهد.

🆔 شناسه شما:
"""
        + str(message.from_user.id)
    )