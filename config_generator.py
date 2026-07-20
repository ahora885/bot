import random
import string


def generate_config(user_id, volume, days):

    code = "".join(
        random.choices(
            string.ascii_letters + string.digits,
            k=12
        )
    )

    config = f"""
🔐 کانفیگ شما

👤 کاربر:
{user_id}

📦 حجم:
{volume} گیگ

⏳ مدت:
{days} روز

🆔 کد:
{code}
"""

    return config