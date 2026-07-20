from aiogram import Router, types
from sqlalchemy import select, func

from database import AsyncSessionLocal, User, Order
from config import ADMIN_ID


router = Router()



@router.message(lambda message: message.text == "👨‍💻 پنل ادمین")
async def admin_panel(message: types.Message):

    if message.from_user.id != ADMIN_ID:

        await message.answer(
            "❌ شما دسترسی ادمین ندارید."
        )

        return


    async with AsyncSessionLocal() as session:

        users = await session.execute(
            select(func.count(User.id))
        )

        orders = await session.execute(
            select(func.count(Order.id))
        )


        user_count = users.scalar()
        order_count = orders.scalar()


    await message.answer(
        f"""
👨‍💻 پنل مدیریت

👥 تعداد کاربران:
{user_count}

📦 تعداد سفارش‌ها:
{order_count}
"""
    )
