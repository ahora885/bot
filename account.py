from aiogram import Router, types

from database import Session, User


router = Router()


@router.message(lambda message: message.text == "👤 اطلاعات حساب")
async def account_handler(message: types.Message):

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
👤 اطلاعات حساب کاربری

🆔 آیدی تلگرام:
{user.telegram_id}

👤 اسم:
{user.first_name}

📛 یوزرنیم:
@{user.username if user.username else "ندارد"}

💰 موجودی کیف پول:
{user.wallet} تومان

🆓 تعداد تست استفاده شده:
{user.free_test_count}/3

📦 تعداد کانفیگ خریداری شده:
{user.configs}
"""
    )


    db.close()
