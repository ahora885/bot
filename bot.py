import telebot
from telebot import types
import sqlite3
import random
import datetime
import os

# =====================
# تنظیمات
# =====================
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
    last_daily TEXT,
    vip_expire TEXT,
    last_request TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount INTEGER,
    status TEXT DEFAULT 'pending',
    date TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS cashbox (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount INTEGER,
    type TEXT,
    user_id INTEGER,
    description TEXT,
    date TEXT
)
""")

conn.commit()

# =====================
# عضویت اجباری
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

        bot.send_message(
            m.chat.id,
            "🚫 شما عضو کانال نیستید یا از کانال خارج شدید!\n\n❌ ربات برای شما قفل شده است.",
            reply_markup=markup
        )
        return True
    return False

# =====================
# کاربران
# =====================
def get_user(user_id):
    cur.execute("SELECT coins, last_daily, vip_expire FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()

    if not row:
        cur.execute("INSERT INTO users VALUES (?, 3, NULL, NULL, NULL)", (user_id,))
        conn.commit()
        return 3, None, None

    return row


def add_coins(user_id, amount):
    coins, _, _ = get_user(user_id)
    coins += amount
    cur.execute("UPDATE users SET coins=? WHERE user_id=?", (coins, user_id))
    conn.commit()


def use_coin(user_id):
    coins, _, _ = get_user(user_id)
    coins -= 1
    cur.execute("UPDATE users SET coins=? WHERE user_id=?", (coins, user_id))
    conn.commit()

# =====================
# VIP
# =====================
def is_vip(user_id):
    _, _, vip = get_user(user_id)
    if not vip:
        return False

    expire = datetime.datetime.strptime(vip, "%Y-%m-%d")
    return expire >= datetime.datetime.now()

# =====================
# روزانه
# =====================
def daily(user_id):
    coins, last, _ = get_user(user_id)

    today = str(datetime.date.today())

    if last == today:
        return 0

    reward = random.randint(1, 3)

    if is_vip(user_id):
        reward += 2

    add_coins(user_id, reward)

    cur.execute("UPDATE users SET last_daily=? WHERE user_id=?", (today, user_id))
    conn.commit()

    return reward

# =====================
# صندوق مالی
# =====================
def add_income(amount, user_id):
    cur.execute("""
    INSERT INTO cashbox (amount, type, user_id, description, date)
    VALUES (?, 'income', ?, 'buy', ?)
    """, (amount, user_id, str(datetime.date.today())))
    conn.commit()


def balance():
    cur.execute("SELECT SUM(amount) FROM cashbox WHERE type='income'")
    inc = cur.fetchone()[0] or 0

    cur.execute("SELECT SUM(amount) FROM cashbox WHERE type='withdraw'")
    out = cur.fetchone()[0] or 0

    return inc - out

# =====================
# ضد اسپم خرید
# =====================
def can_request(user_id):
    cur.execute("SELECT last_request FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()

    today = str(datetime.date.today())

    if row and row[0] == today:
        return False

    cur.execute("UPDATE users SET last_request=? WHERE user_id=?", (today, user_id))
    conn.commit()

    return True

# =====================
# خرید
# =====================
def create_request(user_id, amount):

    if not can_request(user_id):
        bot.send_message(user_id, "❌ روزی فقط 1 خرید")
        return

    cur.execute("""
    INSERT INTO payments (user_id, amount, status, date)
    VALUES (?, ?, 'pending', ?)
    """, (user_id, amount, str(datetime.date.today())))

    conn.commit()

    bot.send_message(user_id, "⏳ درخواست ثبت شد")

    bot.send_message(
        ADMIN_ID,
        f"💳 خرید جدید\n👤 {user_id}\n💰 {amount}\n\n/approve {user_id}\n/reject {user_id}"
    )

# =====================
# START
# =====================
@bot.message_handler(commands=["start"])
def start(m):

    if block_if_left(m):
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("💰 سکه", "🎁 روزانه")
    markup.row("📦 کانفیگ", "💳 خرید")
    markup.row("👨‍💻 پنل ادمین")

    first_name = m.from_user.first_name or "کاربر"

    bot.send_message(
        m.chat.id,
        f"سلام {first_name} به ربات ساخت کانفیگ خوش اومدی 👋",
        reply_markup=markup
    )

# =====================
# سکه
# =====================
@bot.message_handler(func=lambda m: m.text == "💰 سکه")
def coins(m):

    if block_if_left(m):
        return

    c, _, _ = get_user(m.from_user.id)
    bot.send_message(m.chat.id, f"💰 {c}")

# =====================
# روزانه
# =====================
@bot.message_handler(func=lambda m: m.text == "🎁 روزانه")
def d(m):

    if block_if_left(m):
        return

    r = daily(m.from_user.id)
    bot.send_message(m.chat.id, f"🎁 +{r}")

# =====================
# کانفیگ
# =====================
@bot.message_handler(func=lambda m: m.text == "📦 کانفیگ")
def cfg(m):

    if block_if_left(m):
        return

    coins, _, _ = get_user(m.from_user.id)

    if not is_vip(m.from_user.id) and coins < 1:
        bot.send_message(m.chat.id, "❌ سکه نداری")
        return

    if not is_vip(m.from_user.id):
        use_coin(m.from_user.id)

    bot.send_message(m.chat.id, random.choice(CONFIGS))

# =====================
# خرید
# =====================
@bot.message_handler(func=lambda m: m.text == "💳 خرید")
def buy(m):

    if block_if_left(m):
        return

    bot.send_message(m.chat.id, "/buy1 /buy2 /buy3")

@bot.message_handler(commands=["buy1"])
def b1(m): create_request(m.from_user.id, 10)

@bot.message_handler(commands=["buy2"])
def b2(m): create_request(m.from_user.id, 25)

@bot.message_handler(commands=["buy3"])
def b3(m): create_request(m.from_user.id, 50)

# =====================
# پنل ادمین
# =====================
def admin_panel():
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("💰 صندوق", callback_data="cashbox"),
        types.InlineKeyboardButton("📊 گزارش", callback_data="report")
    )
    return markup


@bot.message_handler(func=lambda m: m.text == "👨‍💻 پنل ادمین")
def panel(m):

    if m.from_user.id != ADMIN_ID:
        return

    bot.send_message(m.chat.id, "🧠 پنل ادمین", reply_markup=admin_panel())

# =====================
# callback
# =====================
@bot.callback_query_handler(func=lambda call: True)
def callback(call):

    if call.from_user.id != ADMIN_ID:
        return

    if call.data == "cashbox":
        bot.send_message(call.message.chat.id, f"💰 صندوق: {balance()}")

    elif call.data == "report":
        today = str(datetime.date.today())

        cur.execute("""
        SELECT SUM(amount) FROM cashbox
        WHERE type='income' AND date=?
        """, (today,))

        income = cur.fetchone()[0] or 0

        bot.send_message(call.message.chat.id, f"📊 امروز: {income}")

# =====================
# تایید خرید
# =====================
@bot.message_handler(commands=["approve"])
def approve(m):

    if m.from_user.id != ADMIN_ID:
        return

    user_id = int(m.text.split()[1])

    cur.execute("""
    SELECT amount FROM payments
    WHERE user_id=? AND status='pending'
    ORDER BY id DESC LIMIT 1
    """, (user_id,))

    row = cur.fetchone()

    if not row:
        return

    amount = row[0]

    add_coins(user_id, amount)
    add_income(amount * 1000, user_id)

    cur.execute("UPDATE payments SET status='done' WHERE user_id=?", (user_id,))
    conn.commit()

    bot.send_message(user_id, f"✅ +{amount}")

# =====================
# رد خرید
# =====================
@bot.message_handler(commands=["reject"])
def reject(m):

    if m.from_user.id != ADMIN_ID:
        return

    user_id = int(m.text.split()[1])

    cur.execute("UPDATE payments SET status='rejected' WHERE user_id=?", (user_id,))
    conn.commit()

    bot.send_message(user_id, "❌ رد شد")

# =====================
# اجرا
# =====================
print("BOT RUNNING...")
bot.infinity_polling()
