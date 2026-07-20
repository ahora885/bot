from aiogram import Router, types

router = Router()


@router.message(lambda message: message.text == "👤 اطلاعات حساب")
async def account_handler(message: types.Message):

    await message.answer(
        f"""
👤 اطلاعات حساب کاربری

🆔 آیدی تلگرام:
{message.from_user.id}

👤 اسم:
{message.from_user.first_name}

📛 یوزرنیم:
@{message.from_user.username if message.from_user.username else "ندارد"}

📦 کانفیگ خریداری شده:
0

🆓 تست باقی مانده:
3
"""
    )