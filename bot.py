import telebot
from telebot import types
import sqlite3
import threading
import os
from flask import Flask, jsonify, render_template_string
from openai import OpenAI
import random

TOKEN = os.getenv("TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TOKEN:
    raise ValueError("TOKEN missing")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
client = OpenAI(api_key=OPENAI_API_KEY)

ADMIN_ID = 1183522329

# ================= DB =================
conn = sqlite3.connect("final.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS users (
user_id INTEGER PRIMARY KEY,
coins INTEGER DEFAULT 10,
style TEXT DEFAULT 'neutral'
)""")

cur.execute("""CREATE TABLE IF NOT EXISTS products (
id INTEGER PRIMARY KEY AUTOINCREMENT,
seller_id INTEGER,
title TEXT,
price INTEGER
)""")

cur.execute("""CREATE TABLE IF NOT EXISTS support (
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
message TEXT
)""")

cur.execute("""CREATE TABLE IF NOT EXISTS orders (
id INTEGER PRIMARY KEY AUTOINCREMENT,
buyer_id INTEGER,
product_id INTEGER
)""")

conn.commit()
def get_user(uid):
    cur.execute("SELECT coins FROM users WHERE user_id=?", (uid,))
    r = cur.fetchone()

    if not r:
        style = random.choice(["friendly", "robotic", "funny", "serious"])
        cur.execute("INSERT INTO users (user_id,coins,style) VALUES (?,?,?)",
                    (uid,10,style))
        conn.commit()
        return 10

    return r[0]


def get_style(uid):
    cur.execute("SELECT style FROM users WHERE user_id=?", (uid,))
    r = cur.fetchone()
    return r[0] if r else "neutral"


def ai_reply(uid, text):

    style = get_style(uid)

    system_prompt = f"""
You are a UNIQUE AI assistant.

User style: {style}

Rules:
- Never repeat same answer
- Change tone based on style
- Be creative
- Act like different personality per user
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]
    )

    return res.choices[0].message.content
    def menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("💰 Coins", "🛍 Store")
    kb.row("🛒 Buy", "🏪 Sell")
    kb.row("📞 Support", "🤖 AI")
    kb.row("👑 Admin")
    return kb


# ================= START =================
@bot.message_handler(commands=["start"])
def start(m):
    get_user(m.from_user.id)
    bot.send_message(m.chat.id, "🚀 ULTRA AI SYSTEM ONLINE", reply_markup=menu())


# ================= COINS =================
@bot.message_handler(func=lambda m: m.text == "💰 Coins")
def coins(m):
    bot.send_message(m.chat.id, f"💰 {get_user(m.from_user.id)}")


# ================= STORE =================
@bot.message_handler(func=lambda m: m.text == "🛍 Store")
def store(m):

    cur.execute("SELECT * FROM products")
    rows = cur.fetchall()

    text = "🛍 MARKET:\n\n"
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
            "INSERT INTO products (seller_id,title,price) VALUES (?,?,?)",
            (m.from_user.id, t, int(p))
        )

        conn.commit()
        bot.send_message(m.chat.id, "✅ Added")
    except:
        bot.send_message(m.chat.id, "❌ format: title price")


# ================= BUY =================
@bot.message_handler(func=lambda m: m.text == "🛒 Buy")
def buy(m):

    cur.execute("SELECT * FROM products")
    rows = cur.fetchall()

    text = "🛒 ITEMS:\n\n"
    for r in rows:
        text += f"{r[0]} | {r[2]} = {r[3]}💰\n"

    bot.send_message(m.chat.id, text)
    bot.register_next_step_handler(m, process_buy)


def process_buy(m):
    try:
        pid = int(m.text)

        cur.execute("SELECT price FROM products WHERE id=?", (pid,))
        item = cur.fetchone()

        if not item:
            return bot.send_message(m.chat.id, "❌ Not found")

        price = item[0]
        coins = get_user(m.from_user.id)

        if coins < price:
            return bot.send_message(m.chat.id, "❌ Not enough coins")

        cur.execute("UPDATE users SET coins=? WHERE user_id=?",
                    (coins - price, m.from_user.id))

        cur.execute("INSERT INTO orders (buyer_id,product_id) VALUES (?,?)",
                    (m.from_user.id, pid))

        conn.commit()

        bot.send_message(m.chat.id, "✅ Purchased")

    except:
        bot.send_message(m.chat.id, "❌ error")


# ================= SUPPORT =================
@bot.message_handler(func=lambda m: m.text == "📞 Support")
def support(m):
    msg = bot.send_message(m.chat.id, "Write issue:")
    bot.register_next_step_handler(msg, save_support)


def save_support(m):
    cur.execute(
        "INSERT INTO support (user_id,message) VALUES (?,?)",
        (m.from_user.id, m.text)
    )
    conn.commit()

    bot.send_message(m.chat.id, "📨 Sent to admin")


# ================= AI (PERSONAL CHAT) =================
@bot.message_handler(func=lambda m: m.text == "🤖 AI")
def ai(m):
    msg = bot.send_message(m.chat.id, "Ask me anything:")
    bot.register_next_step_handler(msg, ai_handler)


def ai_handler(m):
    reply = ai_reply(m.from_user.id, m.text)
    bot.send_message(m.chat.id, reply)


# ================= ADMIN =================
@bot.message_handler(func=lambda m: m.text == "👑 Admin")
def admin(m):

    if m.from_user.id != ADMIN_ID:
        return

    cur.execute("SELECT * FROM support")
    rows = cur.fetchall()

    text = "👑 SUPPORT LIST:\n\n"
    for r in rows:
        text += f"{r}\n"

    bot.send_message(m.chat.id, text)


# ================= CLOUD API =================
@app.route("/api")
def api():

    cur.execute("SELECT COUNT(*) FROM users")
    u = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM products")
    p = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM orders")
    o = cur.fetchone()[0]

    return jsonify({
        "status": "online",
        "users": u,
        "products": p,
        "orders": o
    })


@app.route("/")
def home():
    return render_template_string("""
    <h1>🚀 ULTRA AI PLATFORM ONLINE</h1>
    <p>System Running...</p>
    """)


# ================= RUN =================
def run_bot():
    bot.infinity_polling()

def run_web():
    app.run(host="0.0.0.0", port=5000)

threading.Thread(target=run_bot).start()
threading.Thread(target=run_web).start()
