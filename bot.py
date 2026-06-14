import telebot
from telebot import types
import sqlite3
import threading
import os
import time
from flask import Flask, jsonify
from openai import OpenAI

# ================= CONFIG =================
TOKEN = os.getenv("TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TOKEN:
    raise ValueError("TOKEN missing")

bot = telebot.TeleBot(TOKEN, threaded=True, skip_pending=True)
app = Flask(__name__)
client = OpenAI(api_key=OPENAI_API_KEY)

ADMIN_ID = 1183522329


# ================= DATABASE =================
conn = sqlite3.connect("god_all.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
user_id INTEGER PRIMARY KEY,
coins INTEGER DEFAULT 10,
xp INTEGER DEFAULT 0,
level INTEGER DEFAULT 1,
vip INTEGER DEFAULT 0,
lang TEXT DEFAULT 'en'
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS products (
id INTEGER PRIMARY KEY AUTOINCREMENT,
seller_id INTEGER,
title TEXT,
price INTEGER
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS support (
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
message TEXT
)
""")

conn.commit()


# ================= LANGUAGE =================
def detect_lang(text):
    if not text:
        return "en"

    fa = ["سلام", "چطوری", "ربات", "خوبی"]
    ar = ["مرحبا", "كيف"]

    if any(w in text for w in fa):
        return "fa"
    if any(w in text for w in ar):
        return "ar"
    return "en"


def system_prompt(lang):
    if lang == "fa":
        return "تو یک دستیار هوشمند فارسی هستی. کوتاه و طبیعی جواب بده."
    if lang == "ar":
        return "أنت مساعد ذكي. أجب بشكل مختصر."
    return "You are a smart AI assistant. Reply naturally."


# ================= AI =================
def ai_reply(uid, text):
    try:
        lang = detect_lang(text)

        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt(lang)},
                {"role": "user", "content": text}
            ]
        )

        return res.choices[0].message.content

    except Exception as e:
        print("AI ERROR:", e)
        return "⚠️ AI temporarily unavailable"


# ================= USER SYSTEM (FIXED) =================
def ensure_user(uid):
    cur.execute("SELECT user_id FROM users WHERE user_id=?", (uid,))
    if not cur.fetchone():
        cur.execute(
            "INSERT INTO users (user_id, coins, xp, level, vip, lang) VALUES (?,?,?,?,?,?)",
            (uid, 10, 0, 1, 0, "en")
        )
        conn.commit()


def get_user(uid):
    cur.execute("SELECT coins, xp, level, vip FROM users WHERE user_id=?", (uid,))
    r = cur.fetchone()
    return r if r else (10, 0, 1, 0)


# ================= SPAM CHECK =================
def is_spam(text):
    return len(text) < 3 or text.count("!") > 5


# ================= MENU =================
def menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("💰 Coins", "⭐ VIP")
    kb.row("🛍 Store", "🛒 Buy")
    kb.row("🏪 Sell", "🤖 AI")
    kb.row("📞 Support", "👑 Admin")
    return kb


# ================= START =================
@bot.message_handler(commands=["start"])
def start(m):
    ensure_user(m.from_user.id)
    bot.send_message(m.chat.id, "🚀 GOD ALL-IN-ONE SYSTEM ONLINE", reply_markup=menu())


# ================= COINS =================
@bot.message_handler(func=lambda m: m.text == "💰 Coins")
def coins(m):
    c, xp, lvl, vip = get_user(m.from_user.id)
    bot.send_message(m.chat.id, f"💰 Coins: {c}")


# ================= VIP =================
@bot.message_handler(func=lambda m: m.text == "⭐ VIP")
def vip(m):
    c, xp, lvl, vip = get_user(m.from_user.id)
    bot.send_message(m.chat.id, "👑 VIP ACTIVE" if vip else "❌ Not VIP")


# ================= STORE =================
@bot.message_handler(func=lambda m: m.text == "🛍 Store")
def store(m):
    cur.execute("SELECT * FROM products")
    rows = cur.fetchall()

    if not rows:
        return bot.send_message(m.chat.id, "Empty store")

    text = "🛍 STORE:\n\n"
    for r in rows:
        text += f"{r[0]} | {r[2]} | {r[3]}💰\n"

    bot.send_message(m.chat.id, text)


# ================= SELL =================
@bot.message_handler(func=lambda m: m.text == "🏪 Sell")
def sell(m):
    msg = bot.send_message(m.chat.id, "Send: title price")
    bot.register_next_step_handler(msg, save_product)


def save_product(m):
    try:
        t, p = m.text.split()
        cur.execute(
            "INSERT INTO products (seller_id, title, price) VALUES (?,?,?)",
            (m.from_user.id, t, int(p))
        )
        conn.commit()
        bot.send_message(m.chat.id, "✅ Added")
    except Exception as e:
        print("SELL ERROR:", e)
        bot.send_message(m.chat.id, "❌ format error")


# ================= BUY =================
@bot.message_handler(func=lambda m: m.text == "🛒 Buy")
def buy(m):
    cur.execute("SELECT * FROM products")
    rows = cur.fetchall()

    if not rows:
        return bot.send_message(m.chat.id, "No items")

    text = "🛒 ITEMS:\n\n"
    for r in rows:
        text += f"{r[0]} | {r[2]} = {r[3]}💰\n"

    bot.send_message(m.chat.id, text)


# ================= SUPPORT =================
@bot.message_handler(func=lambda m: m.text == "📞 Support")
def support(m):
    msg = bot.send_message(m.chat.id, "Write issue:")
    bot.register_next_step_handler(msg, save_support)


def save_support(m):
    try:
        if is_spam(m.text):
            return bot.send_message(m.chat.id, "⚠️ Spam detected")

        cur.execute(
            "INSERT INTO support (user_id, message) VALUES (?,?)",
            (m.from_user.id, m.text)
        )
        conn.commit()

        bot.send_message(m.chat.id, "📨 Sent")

    except Exception as e:
        print("SUPPORT ERROR:", e)


# ================= AI CHAT =================
@bot.message_handler(func=lambda m: m.text == "🤖 AI")
def ai(m):
    msg = bot.send_message(m.chat.id, "Ask:")
    bot.register_next_step_handler(msg, ai_step)


def ai_step(m):
    bot.send_message(m.chat.id, ai_reply(m.from_user.id, m.text))


# ================= ADMIN =================
@bot.message_handler(func=lambda m: m.text == "👑 Admin")
def admin(m):
    if m.from_user.id != ADMIN_ID:
        return

    cur.execute("SELECT * FROM support")
    rows = cur.fetchall()

    text = "📞 SUPPORT:\n\n"
    for r in rows:
        text += f"{r}\n"

    bot.send_message(m.chat.id, text)


# ================= FLASK API =================
@app.route("/")
def home():
    return jsonify({"status": "GOD SYSTEM ONLINE"})


@app.route("/stats")
def stats():
    cur.execute("SELECT COUNT(*) FROM users")
    u = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM products")
    p = cur.fetchone()[0]

    return jsonify({
        "users": u,
        "products": p
    })


# ================= SAFE RUN =================
def run_bot():
    while True:
        try:
            bot.infinity_polling(skip_pending=True)
        except Exception as e:
            print("BOT RESTART:", e)
            time.sleep(3)


def run_web():
    app.run(host="0.0.0.0", port=5000, use_reloader=False)


threading.Thread(target=run_bot).start()
threading.Thread(target=run_web).start()
