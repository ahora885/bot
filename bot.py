import telebot
from telebot import types
import sqlite3
import datetime
import os
import time
from flask import Flask, jsonify
import threading

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 1183522329
CHANNEL = "@config_v2ray_mpt"

bot = telebot.TeleBot(TOKEN)

conn = sqlite3.connect("bot.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
user_id INTEGER PRIMARY KEY,
coins INTEGER DEFAULT 3,
last_daily INTEGER DEFAULT 0,
vip_type TEXT,
vip_expire TEXT,
banned INTEGER DEFAULT 0,
last_action INTEGER DEFAULT 0
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS sources (
id INTEGER PRIMARY KEY AUTOINCREMENT,
title TEXT,
price INTEGER,
file_id TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS payments (
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
amount INTEGER,
type TEXT,
date TEXT
)
""")

conn.commit()


def log(uid, action):
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(f"{uid} | {action} | {datetime.datetime.now()}\n")


def anti_spam(uid):
    now = int(time.time())
    cur.execute("SELECT last_action FROM users WHERE user_id=?", (uid,))
    r = cur.fetchone()
    last = r[0] if r else 0
    if now - last < 2:
        return False
    cur.execute("UPDATE users SET last_action=? WHERE user_id=?", (now, uid))
    conn.commit()
    return True


def get_user(uid):
    cur.execute("SELECT coins,last_daily FROM users WHERE user_id=?", (uid,))
    r = cur.fetchone()
    if not r:
        cur.execute("INSERT INTO users VALUES (?,3,0,NULL,NULL,0,0)", (uid,))
        conn.commit()
        return 3, 0
    return r


def is_banned(uid):
    cur.execute("SELECT banned FROM users WHERE user_id=?", (uid,))
    r = cur.fetchone()
    return r and r[0] == 1


def add_payment(uid, amount, typ):
    cur.execute("INSERT INTO payments VALUES (NULL,?,?,?,?)",
                (uid, amount, typ, str(datetime.datetime.now())))
    conn.commit()
@bot.message_handler(commands=["start"])
def start(m):
    if is_banned(m.from_user.id):
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("💰 سکه", "🎁 روزانه")
    markup.row("📂 سورس ها", "💎 خرید سورس")
    markup.row("💎 خرید VIP", "👨‍💻 پنل ادمین")

    bot.send_message(m.chat.id, "👋 مارکت‌پلیس فعال شد", reply_markup=markup)


@bot.message_handler(func=lambda m: m.text == "💰 سکه")
def coins(m):
    if not anti_spam(m.from_user.id):
        return
    c, _ = get_user(m.from_user.id)
    bot.send_message(m.chat.id, f"💰 {c}")


@bot.message_handler(func=lambda m: m.text == "🎁 روزانه")
def daily(m):
    if not anti_spam(m.from_user.id):
        return

    c, last = get_user(m.from_user.id)
    now = int(time.time())
    last = int(last or 0)

    if now - last < 86400:
        bot.send_message(m.chat.id, "⏳ هنوز زوده")
        return

    c += 1
    cur.execute("UPDATE users SET coins=?, last_daily=? WHERE user_id=?",
                (c, now, m.from_user.id))
    conn.commit()

    bot.send_message(m.chat.id, "🎁 +1 سکه")


@bot.message_handler(func=lambda m: m.text == "💎 خرید سورس")
def buy_list(m):
    cur.execute("SELECT id,title,price FROM sources")
    rows = cur.fetchall()

    text = "📦 لیست:\n\n"
    for r in rows:
        text += f"{r[0]} - {r[1]} | {r[2]}\n"

    bot.send_message(m.chat.id, text)
    bot.register_next_step_handler(m, buy_source)


def buy_source(m):
    sid = int(m.text)

    cur.execute("SELECT title,price,file_id FROM sources WHERE id=?", (sid,))
    r = cur.fetchone()

    if not r:
        bot.send_message(m.chat.id, "❌ نیست")
        return

    title, price, file_id = r
    c, _ = get_user(m.from_user.id)

    if c < price:
        bot.send_message(m.chat.id, "❌ کم داری")
        return

    c -= price
    cur.execute("UPDATE users SET coins=? WHERE user_id=?", (c, m.from_user.id))
    conn.commit()

    add_payment(m.from_user.id, price, "source")
    log(m.from_user.id, f"BUY {title}")

    bot.send_document(m.chat.id, open(file_id, "rb"))


@bot.message_handler(func=lambda m: m.text == "👨‍💻 پنل ادمین")
def admin(m):
    if m.from_user.id != ADMIN_ID:
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📊 آمار", "📢 پیام همگانی")
    bot.send_message(m.chat.id, "👨‍💻 پنل", reply_markup=markup)
@bot.message_handler(func=lambda m: m.text == "📊 آمار")
def stats(m):
    cur.execute("SELECT COUNT(*) FROM users")
    u = cur.fetchone()[0] or 0

    cur.execute("SELECT SUM(amount) FROM payments")
    r = cur.fetchone()[0] or 0

    bot.send_message(m.chat.id, f"👥 {u}\n💰 {r}")


@bot.message_handler(func=lambda m: m.text == "📢 پیام همگانی")
def bc(m):
    if m.from_user.id != ADMIN_ID:
        return

    msg = bot.send_message(m.chat.id, "✍ پیام")
    bot.register_next_step_handler(msg, send_bc)


def send_bc(m):
    cur.execute("SELECT user_id FROM users")
    users = cur.fetchall()

    for u in users:
        try:
            bot.send_message(u[0], m.text)
        except:
            pass

    bot.send_message(m.chat.id, "✅ ارسال شد")


app = Flask(__name__)

@app.route("/stats")
def api():
    cur.execute("SELECT COUNT(*) FROM users")
    u = cur.fetchone()[0] or 0

    cur.execute("SELECT SUM(amount) FROM payments")
    r = cur.fetchone()[0] or 0

    return jsonify({"users": u, "revenue": r})


def run():
    app.run(host="0.0.0.0", port=5000)


threading.Thread(target=run, daemon=True).start()

print("🚀 FULL MARKETPLACE READY")
bot.infinity_polling()
