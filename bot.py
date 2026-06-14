import telebot
from telebot import types
import sqlite3
import threading
import datetime
import os
from flask import Flask, render_template_string

# ================= CONFIG =================
TOKEN = os.environ.get("TOKEN")

if not TOKEN:
    raise ValueError(
        "متغیر TOKEN پیدا نشد! توکن ربات را در بخش Variables گیت‌هاب/سرویس خودت با نام TOKEN اضافه کن."
    )

ADMIN_ID = 1183522329

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ================= DB =================
conn = sqlite3.connect("bot.db", check_same_thread=False)
cur = conn.cursor()

# USERS (Wallet + VIP)
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
user_id INTEGER PRIMARY KEY,
coins INTEGER DEFAULT 3,
vip TEXT
)
""")

# PRODUCTS (Marketplace / Amazon style)
cur.execute("""
CREATE TABLE IF NOT EXISTS products (
id INTEGER PRIMARY KEY AUTOINCREMENT,
seller_id INTEGER,
title TEXT,
price INTEGER
)
""")

# SOURCES (Digital store)
cur.execute("""
CREATE TABLE IF NOT EXISTS sources (
id INTEGER PRIMARY KEY AUTOINCREMENT,
title TEXT,
price INTEGER
)
""")

conn.commit()
# ================= CORE USER =================
def get_user(uid):
    cur.execute("SELECT coins FROM users WHERE user_id=?", (uid,))
    r = cur.fetchone()

    if not r:
        cur.execute(
            "INSERT INTO users (user_id,coins,vip) VALUES (?,3,NULL)",
            (uid,)
        )
        conn.commit()
        return 3

    return r[0]


def update_user(uid, coins):
    cur.execute("UPDATE users SET coins=? WHERE user_id=?", (coins, uid))
    conn.commit()


# ================= MENU =================
def menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("💰 Coins", "🛍 Store")
    kb.row("📦 Sources", "🏪 Sell")
    kb.row("👨‍💻 Admin", "🌐 Panel")
    return kb


# ================= START =================
@bot.message_handler(commands=["start"])
def start(m):
    get_user(m.from_user.id)
    bot.send_message(
        m.chat.id,
        "🚀 ALL-IN-ONE SYSTEM READY",
        reply_markup=menu()
    )


# ================= COINS =================
@bot.message_handler(func=lambda m: m.text == "💰 Coins")
def coins(m):
    bot.send_message(m.chat.id, f"💰 {get_user(m.from_user.id)}")


# ================= STORE =================
@bot.message_handler(func=lambda m: m.text == "🛍 Store")
def store(m):
    cur.execute("SELECT * FROM products")
    rows = cur.fetchall()

    text = "🛍 MARKETPLACE:\n\n"
    for r in rows:
        text += f"ID:{r[0]} | {r[2]} | {r[3]}💰\n"

    bot.send_message(m.chat.id, text)


# ================= SOURCES =================
@bot.message_handler(func=lambda m: m.text == "📦 Sources")
def sources(m):
    cur.execute("SELECT * FROM sources")
    rows = cur.fetchall()

    text = "📦 SOURCES:\n\n"
    for r in rows:
        text += f"ID:{r[0]} | {r[1]} | {r[2]}💰\n"

    bot.send_message(m.chat.id, text)


# ================= SELL SYSTEM =================
@bot.message_handler(func=lambda m: m.text == "🏪 Sell")
def sell(m):
    msg = bot.send_message(m.chat.id, "Send: title price")
    bot.register_next_step_handler(msg, save)


def save(m):
    try:
        title, price = m.text.split()

        cur.execute("""
        INSERT INTO products (seller_id,title,price)
        VALUES (?,?,?)
        """, (m.from_user.id, title, int(price)))

        conn.commit()
        bot.send_message(m.chat.id, "✅ Added to marketplace")

    except:
        bot.send_message(m.chat.id, "❌ format: title price")


# ================= ADMIN PANEL =================
@bot.message_handler(func=lambda m: m.text == "👨‍💻 Admin")
def admin(m):
    if m.from_user.id != ADMIN_ID:
        return

    cur.execute("SELECT * FROM users")
    users = cur.fetchall()

    text = "👨‍💻 USERS:\n\n"
    for u in users:
        text += f"{u}\n"

    bot.send_message(m.chat.id, text)
    
    # ================= WEB PANEL =================
@app.route("/")
def home():

    cur.execute("SELECT COUNT(*) FROM users")
    u = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM products")
    p = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM sources")
    s = cur.fetchone()[0]

    return render_template_string("""
    <html>
    <body style="background:#0f0f0f;color:white;font-family:Arial">
        <h1>🚀 PRO ALL-IN-ONE DASHBOARD</h1>
        <p>👤 Users: {{u}}</p>
        <p>🛍 Products: {{p}}</p>
        <p>📦 Sources: {{s}}</p>
    </body>
    </html>
    """, u=u, p=p, s=s)


@app.route("/users")
def users():

    cur.execute("SELECT * FROM users")
    rows = cur.fetchall()

    return render_template_string("""
    <html><body style="background:#111;color:white">
    <h2>USERS</h2>
    {% for u in users %}
    <p>{{u}}</p>
    {% endfor %}
    </body></html>
    """, users=rows)


# ================= RUN BOTH =================
def run_bot():
    print("BOT RUNNING")
    bot.infinity_polling()


def run_web():
    print("WEB RUNNING")
    app.run(host="0.0.0.0", port=5000)


threading.Thread(target=run_bot).start()
threading.Thread(target=run_web).start()
