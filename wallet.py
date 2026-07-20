from aiogram import Router, types

from database import Session, User


router = Router()


@router.message(lambda message: message.text == "💰 کیف پول")
async def wallet_handler(message: types.Message):

    db = Session()

    user = db.query(User).filter(
        User.telegram_id == message.from_user.id
    ).first()


    if not user:
        await message.answer(
            "❌ ابتدا ربات را با /start شروع کنید."
        )
        db.close()
        return


    await message.answer(
        f"""
💰 کیف پول شما

💵 موجودی:
{user.wallet} تومان

📦 تعداد کانفیگ خریداری شده:
{user.configs}

🧾 وضعیت:
فعال
"""
    )


    db.close()
