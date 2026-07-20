from aiogram import Router, types

from sqlalchemy import select

from database import AsyncSessionLocal, User


router = Router()


@router.message(lambda message: message.text == "👤 اطلاعات حساب")
async def account_handler(message: types.Message):

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(User).where(
                User.telegram_id == message.from_user.id
            )
        )

        user = result.scalar_one_or_none()


        if not user:

            await message.answer(
                "❌ ابتدا ربات را با /start شروع کنید."
            )

            return


        await message.answer(
            f"""
👤 اطلاعات حساب کاربری

🆔 آیدی تلگرام:
{user.telegram_id}

👤 اسم:
{user.first_name or "ندارد"}

📛 یوزرنیم:
@{user.username if user.username else "ندارد"}

💰 موجودی کیف پول:
{user.wallet} تومان

🆓 تست رایگان:
{user.free_test_count}/3

📦 تعداد کانفیگ:
{user.configs}
"""
        )
