from aiogram import Router, types
from aiogram.filters import Command

from config import ADMIN_ID

router = Router()


@router.message(Command("admin"))
async def admin_panel(message: types.Message):

    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ دسترسی ندارید.")
        return

    await message.answer(
        """
👨‍💻 پنل مدیریت

امکانات در حال آماده‌سازی:

👥 کاربران
📦 کانفیگ‌ها
💰 کیف پول‌ها
📊 آمار
📢 ارسال همگانی
"""
    )