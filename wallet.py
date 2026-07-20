from aiogram import Router, types

from sqlalchemy import select

from database import AsyncSessionLocal, User


router = Router()


@router.message(lambda message: message.text == "💰 کیف پول")
async def wallet_handler(message: types.Message):

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
💰 کیف پول شما

💵 موجودی:
{user.wallet} تومان

📦 تعداد کانفیگ خریداری شده:
{user.configs}

🎁 هدیه ورود:
{"دریافت شده" if user.welcome_bonus else "دریافت نشده"}
"""
        )
