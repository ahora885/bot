import telebot
from telebot import types
import sqlite3
import random
import datetime
import os

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 1183522329
CHANNEL = "@config_v2ray_mpt"

bot = telebot.TeleBot(TOKEN)

CONFIGS = ["CONFIG_1", "CONFIG_2", "CONFIG_3"]

# =====================
# دیتابیس
# =====================
conn = sqlite3.connect("bot.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
user_id INTEGER PRIMARY KEY,
coins INTEGER DEFAULT 3,
last_daily INTEGER,
vip_expire TEXT,
last_request TEXT
)
""")

conn.commit()

# =====================
# عضویت
# =====================
def is_member(user_id):
    try:
        status = bot.get_chat_member(CHANNEL, user_id).status
        return status in ["member", "creator", "administrator"]
    except:
        return False


def block_if_left(m):
    if not is_member(m.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton(
                "📢 عضویت در کانال",
                url=f"https://t.me/{CHANNEL.replace('@','')}"
            )
        )
        bot.send_message(m.chat.id, "🚫 اول عضو کانال شو", reply_markup=markup)
        return True
    return False

# =====================
# کاربران
# =====================
def get_user(user_id):
    cur.execute("SELECT coins, last_daily FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()

    if not row:
        cur.execute("INSERT INTO users VALUES (?, 3, NULL, NULL, NULL)", (user_id,))
        conn.commit()
        return 3, None

    return row


def add_coins(user_id, amount):
    coins, last = get_user(user_id)
    coins += amount
    cur.execute("UPDATE users SET coins=? WHERE user_id=?", (coins, user_id))
    conn.commit()


# =====================
# روزانه + تایمر
# =====================
def daily(user_id):
    coins, last = get_user(user_id)

    now = int(datetime.datetime.now().timestamp())

    if last:
        diff = now - int(last)

        if diff < 86400:
            remain = 86400 - diff

            hours = remain // 3600
            minutes = (remain % 3600) // 60

            return ("wait", f"{hours} ساعت و {minutes} دقیقه")

    add_coins(user_id, 1)

    cur.execute(
        "UPDATE users SET last_daily=? WHERE user_id=?",
        (now, user_id)
    )
    conn.commit()

    return ("ok", None)

# =====================
# start
# =====================
@bot.message_handler(commands=["start"])
def start(m):

    if block_if_left(m):
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("💰 سکه", "🎁 روزانه")
    markup.row("📦 کانفیگ")
    markup.row("👨‍💻 پنل ادمین")

    bot.send_message(m.chat.id, "سلام 👋", reply_markup=markup)

# =====================
# سکه
# =====================
@bot.message_handler(func=lambda m: m.text == "💰 سکه")
def coins(m):

    if block_if_left(m):
        return

    c, _ = get_user(m.from_user.id)
    bot.send_message(m.chat.id, f"💰 {c}")

# =====================
# روزانه
# =====================
@bot.message_handler(func=lambda m: m.text == "🎁 روزانه")
def d(m):

    if block_if_left(m):
        return

    status, data = daily(m.from_user.id)

    if status == "ok":
        bot.send_message(m.chat.id, "🎁 +1 سکه")
    else:
        bot.send_message(m.chat.id, f"⏳ تا دریافت بعدی: {data}")

# =====================
# کانفیگ
# =====================
@bot.message_handler(func=lambda m: m.text == "📦 کانفیگ")
def cfg(m):

    if block_if_left(m):
        return

    coins, _ = get_user(m.from_user.id)

    if coins < 1:
        bot.send_message(m.chat.id, "❌ سکه نداری")
        return

    coins -= 1
    cur.execute("UPDATE users SET coins=? WHERE user_id=?", (coins, m.from_user.id))
    conn.commit()

    bot.send_message(m.chat.id, random.choice(CONFIGS))

# =====================
# اجرا
# =====================
print("BOT RUNNING...")
bot.infinity_polling()