import telebot
from telebot import types
import sqlite3
import threading
import os
import time
import logging
from flask import Flask, jsonify
from openai import OpenAI
from collections import defaultdict

# ================= CONFIG =================
TOKEN = os.getenv("TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TOKEN:
    raise ValueError("TOKEN missing")

bot = telebot.TeleBot(TOKEN, threaded=True, skip_pending=True)
app = Flask(__name__)
client = OpenAI(api_key=OPENAI_API_KEY)

ADMIN_ID = 1183522329

# ================= LOGGING =================
logging.basicConfig(level=logging.INFO)

# ================= DATABASE (SAFE MODE) =================
conn = sqlite3.connect("god_production.db", check_same_thread=False, timeout=10)
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

# ================= RATE LIMIT (ANTI SPAM) =================
user_last_msg = defaultdict(float)
RATE_LIMIT_SEC = 3

def is_spam(uid):
    now = time.time()
    if now - user_last_msg[uid] < RATE_LIMIT_SEC:
        return True
    user_last_msg[uid] = now
    return False

# ================= LANGUAGE =================
def detect_lang(text):
    if not text:
        return "en"

    fa_words = ["سلام", "چطوری", "ربات", "خوبی"]
    ar_words = ["مرحبا", "كيف"]

    if any(w in text for w in fa_words):
        return "fa"
    if any(w in text for w in ar_words):
        return "ar"
    return "en"

def system_prompt(lang):
    if lang == "fa":
        return "تو یک دستیار هوشمند فارسی هستی. کوتاه و طبیعی جواب بده."
    if lang == "ar":
        return "أنت مساعد ذكي. أجب بشكل مختصر وطبيعي."
    return "You are a smart AI assistant. Reply clearly and naturally."

# ================= SAFE DB =================
def ensure_user(uid):
    try:
        cur.execute("SELECT user_id FROM users WHERE user_id=?", (uid,))
        if not cur.fetchone():
            cur.execute("""
            INSERT INTO users (user_id, coins, xp, level, vip, lang)
            VALUES (?,10,0,1,0,'en')
            """, (uid,))
            conn.commit()
    except Exception as e:
        logging.error(f"DB error ensure_user: {e}")

def get_user(uid):
    try:
        cur.execute("SELECT coins, xp, level, vip FROM users WHERE user_id=?", (uid,))
        return cur.fetchone() or (10, 0, 1, 0)
    except:
        return (10, 0, 1, 0)

# ================= AI (SAFE + FAST) =================
def ai_reply(uid, text):
    try:
        lang = detect_lang(text)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt(lang)},
                {"role": "user", "content": text}
            ],
            timeout=15
        )

        reply = response.choices[0].message.content

        # XP SYSTEM SAFE
        cur.execute("SELECT xp, level FROM users WHERE user_id=?", (uid,))
        row = cur.fetchone()

        if row:
            xp, lvl = row
            xp += 2

            if xp >= lvl * 10:
                lvl += 1
                xp = 0

            cur.execute("UPDATE users SET xp=?, level=? WHERE user_id=?",
                        (xp, lvl, uid))
            conn.commit()

        return reply

    except Exception as e:
        logging.error(f"AI error: {e}")
        return "⚠️ AI temporarily unavailable"

# ================= MENU =================
def menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("💰 Coins", "📊 Level")
    kb.row("🛍 Store", "🛒 Buy")
    kb.row("🏪 Sell", "🤖 AI")
    kb.row("📞 Support", "👑 Admin")
    return kb

# ================= START =================
@bot.message_handler(commands=["start"])
def start(m):
    ensure_user(m.from_user.id)
    bot.send_message(m.chat.id, "🚀 PRODUCTION GOD FIX ONLINE", reply_markup=menu())

# ================= COINS =================
@bot.message_handler(func=lambda m: m.text == "💰 Coins")
def coins(m):
    if is_spam(m.from_user.id):
        return

    c, xp, lvl, vip = get_user(m.from_user.id)
    bot.send_message(m.chat.id, f"💰 Coins: {c}")

# ================= LEVEL =================
@bot.message_handler(func=lambda m: m.text == "📊 Level")
def level(m):
    if is_spam(m.from_user.id):
        return

    c, xp, lvl, vip = get_user(m.from_user.id)
    bot.send_message(m.chat.id, f"⭐ Level: {lvl}\n⚡ XP: {xp}")

# ================= STORE SAFE =================
@bot.message_handler(func=lambda m: m.text == "🛍 Store")
def store(m):
    try:
        cur.execute("SELECT * FROM products")
        rows = cur.fetchall()

        if not rows:
            return bot.send_message(m.chat.id, "🛍 Store is empty")

        text = "🛍 STORE:\n\n"
        for r in rows:
            text += f"{r[0]} | {r[2]} | {r[3]}💰\n"

        bot.send_message(m.chat.id, text)

    except Exception as e:
        logging.error(e)
        bot.send_message(m.chat.id, "Store error")

# ================= SELL SAFE =================
@bot.message_handler(func=lambda m: m.text == "🏪 Sell")
def sell(m):
    msg = bot.send_message(m.chat.id, "Send: title price")
    bot.register_next_step_handler(msg, save_product)

def save_product(m):
    try:
        t, p = m.text.split()
        cur.execute("""
        INSERT INTO products (seller_id,title,price)
        VALUES (?,?,?)
        """, (m.from_user.id, t, int(p)))
        conn.commit()

        bot.send_message(m.chat.id, "✅ Added")

    except Exception as e:
        logging.error(e)
        bot.send_message(m.chat.id, "❌ format: title price")

# ================= BUY SAFE =================
@bot.message_handler(func=lambda m: m.text == "🛒 Buy")
def buy(m):
    try:
        cur.execute("SELECT * FROM products")
        rows = cur.fetchall()

        if not rows:
            return bot.send_message(m.chat.id, "No items")

        text = "🛒 ITEMS:\n\n"
        for r in rows:
            text += f"{r[0]} | {r[2]} = {r[3]}💰\n"

        bot.send_message(m.chat.id, text)

    except Exception as e:
        logging.error(e)

# ================= SUPPORT SAFE =================
@bot.message_handler(func=lambda m: m.text == "📞 Support")
def support(m):
    msg = bot.send_message(m.chat.id, "Write issue:")
    bot.register_next_step_handler(msg, save_support)

def save_support(m):
    try:
        if is_spam(m.from_user.id):
            return bot.send_message(m.chat.id, "⚠️ Slow down")

        cur.execute("""
        INSERT INTO support (user_id,message)
        VALUES (?,?)
        """, (m.from_user.id, m.text))
        conn.commit()

        bot.send_message(m.chat.id, "📨 Sent")

    except Exception as e:
        logging.error(e)

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

    text = "📞 SUPPORT LOGS:\n\n"
    for r in rows:
        text += f"{r}\n"

    bot.send_message(m.chat.id, text)

# ================= FLASK =================
@app.route("/")
def home():
    return jsonify({"status": "PRODUCTION GOD FIX ONLINE"})

@app.route("/stats")
def stats():
    cur.execute("SELECT COUNT(*) FROM users")
    u = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM products")
    p = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM support")
    s = cur.fetchone()[0]

    return jsonify({
        "users": u,
        "products": p,
        "support": s
    })

# ================= SAFE RUNNER =================
def run_bot():
    while True:
        try:
            bot.infinity_polling(skip_pending=True, timeout=10, long_polling_timeout=5)
        except Exception as e:
            logging.error(f"BOT CRASH RECOVERED: {e}")
            time.sleep(3)

def run_web():
    app.run(host="0.0.0.0", port=5000, use_reloader=False)

threading.Thread(target=run_bot).start()
threading.Thread(target=run_web).start()
