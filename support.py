from aiogram import Router, types

from config import ADMIN_ID


router = Router()



@router.message(lambda message: message.text == "💬 پشتیبانی")
async def support_start(message: types.Message):

    await message.answer(
        """
💬 پشتیبانی

برای ارتباط با پشتیبانی، پیام خود را ارسال کنید.

پیام شما مستقیم برای مدیریت ارسال می‌شود.
"""
    )



@router.message()
async def send_to_admin(message: types.Message):

    if message.from_user.id == ADMIN_ID:
        return


    await message.bot.send_message(
        ADMIN_ID,
        f"""
📩 پیام جدید پشتیبانی

👤 کاربر:
{message.from_user.full_name}

🆔 آیدی:
{message.from_user.id}


💬 پیام:
{message.text}
"""
    )


    await message.answer(
        "✅ پیام شما برای پشتیبانی ارسال شد."
    )
