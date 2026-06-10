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
vip_type TEXT
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

# =====================
# VIP check
# =====================
def is_vip(user_id):
    cur.execute("SELECT vip_expire FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()

    if not row or not row[0]:
        return False

    try:
        exp = datetime.datetime.strptime(row[0], "%Y-%m-%d")
        return exp >= datetime.datetime.now()
    except:
        return False


def set_vip(user_id, vip_type):
    expire = datetime.datetime.now() + datetime.timedelta(days=30)
    cur.execute(
        "UPDATE users SET vip_type=?, vip_expire=? WHERE user_id=?",
        (vip_type, expire.strftime("%Y-%m-%d"), user_id)
    )
    conn.commit()

# =====================
# روزانه
# =====================
def daily(user_id):
    coins, last = get_user(user_id)

    now = int(datetime.datetime.now().timestamp())

    if last:
        diff = now - int(last)
        if diff < 86400:
            remain = 86400 - diff
            return ("wait", f"{remain//3600} ساعت و {(remain%3600)//60} دقیقه")

    coins += 1
    cur.execute("UPDATE users SET coins=? WHERE user_id=?", (coins, user_id))
    cur.execute("UPDATE users SET last_daily=? WHERE user_id=?", (now, user_id))
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
    markup.row("💎 خرید VIP")
    markup.row("👨‍💻 پنل ادمین")

    bot.send_message(m.chat.id, "سلام 👋", reply_markup=markup)

# =====================
# سکه
# =====================
@bot.message_handler(func=lambda m: m.text == "💰 سکه")
def coins(m):
    c, _ = get_user(m.from_user.id)
    bot.send_message(m.chat.id, f"💰 {c}")

# =====================
# روزانه
# =====================
@bot.message_handler(func=lambda m: m.text == "🎁 روزانه")
def d(m):

    status, data = daily(m.from_user.id)

    if status == "ok":
        bot.send_message(m.chat.id, "🎁 +1 سکه")
    else:
        bot.send_message(m.chat.id, f"⏳ {data}")

# =====================
# کانفیگ (VIP قیمت)
# =====================
@bot.message_handler(func=lambda m: m.text == "📦 کانفیگ")
def cfg(m):

    coins, _ = get_user(m.from_user.id)
    first = m.from_user.first_name or "کاربر"

    cur.execute("SELECT vip_type FROM users WHERE user_id=?", (m.from_user.id,))
    row = cur.fetchone()
    vip = row[0] if row else None

    if vip == "PRO":
        price = 1
    elif vip == "NORMAL":
        price = 2
    else:
        price = 3

    if coins < price:
        need = price - coins
        bot.send_message(m.chat.id,
            f"👤 {first} شما {coins} سکه دارید\n"
            f"❌ نیاز: {need} سکه\n"
            f"💰 قیمت: {price}"
        )
        return

    coins -= price
    cur.execute("UPDATE users SET coins=? WHERE user_id=?", (coins, m.from_user.id))
    conn.commit()

    bot.send_message(m.chat.id, random.choice(CONFIGS))

# =====================
# VIP MENU
# =====================
@bot.message_handler(func=lambda m: m.text == "💎 خرید VIP")
def vip_menu(m):

    markup = types.InlineKeyboardMarkup()

    markup.row(types.InlineKeyboardButton("⭐ VIP معمولی (7 سکه)", callback_data="vip_normal"))
    markup.row(types.InlineKeyboardButton("🔥 VIP PRO (10 سکه)", callback_data="vip_pro"))
    markup.row(types.InlineKeyboardButton("🔄 تمدید VIP", callback_data="vip_extend"))
    markup.row(types.InlineKeyboardButton("🔙 برگشت", callback_data="vip_back"))

    bot.send_message(m.chat.id,
        "💎 میخواهید کدام نوع اشتراک VIP را خریداری کنید؟",
        reply_markup=markup)

# =====================
# ADMIN PANEL
# =====================
@bot.message_handler(func=lambda m: m.text == "👨‍💻 پنل ادمین")
def admin_panel(m):

    if m.from_user.id != ADMIN_ID:
        return

    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("💎 لیست VIP ها", callback_data="vip_list"))

    bot.send_message(m.chat.id, "👨‍💻 پنل ادمین", reply_markup=markup)

# =====================
# CALLBACK
# =====================
@bot.callback_query_handler(func=lambda call: True)
def callback(call):

    coins, _ = get_user(call.from_user.id)

    # VIP خرید
    if call.data == "vip_normal":
        if coins < 7:
            bot.send_message(call.message.chat.id, "❌ 7 سکه لازم است")
            return
        coins -= 7
        cur.execute("UPDATE users SET coins=?, vip_type=? WHERE user_id=?",
                    (coins, "NORMAL", call.from_user.id))
        conn.commit()
        set_vip(call.from_user.id, "NORMAL")
        bot.send_message(call.message.chat.id, "⭐ VIP فعال شد (30 روز)")

    elif call.data == "vip_pro":
        if coins < 10:
            bot.send_message(call.message.chat.id, "❌ 10 سکه لازم است")
            return
        coins -= 10
        cur.execute("UPDATE users SET coins=?, vip_type=? WHERE user_id=?",
                    (coins, "PRO", call.from_user.id))
        conn.commit()
        set_vip(call.from_user.id, "PRO")
        bot.send_message(call.message.chat.id, "🔥 VIP PRO فعال شد (30 روز)")

    # برگشت
    elif call.data == "vip_back":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row("💰 سکه", "🎁 روزانه")
        markup.row("📦 کانفیگ")
        markup.row("💎 خرید VIP")
        markup.row("👨‍💻 پنل ادمین")

        bot.send_message(call.message.chat.id, "🔙 برگشت", reply_markup=markup)

    # لیست VIP
    elif call.data == "vip_list":

        if call.from_user.id != ADMIN_ID:
            return

        cur.execute("SELECT user_id, vip_type, vip_expire FROM users WHERE vip_type IS NOT NULL")
        rows = cur.fetchall()

        text = "💎 VIP ها:\n\n"

        for r in rows:
            text += f"ID:{r[0]} | {r[1]} | {r[2]}\n"

        bot.send_message(call.message.chat.id, text or "هیچ VIPی نیست")

# =====================
# RUN
# =====================
print("BOT RUNNING...")
bot.infinity_polling()