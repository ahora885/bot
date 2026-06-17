import telebot
from telebot import types
import sqlite3
import os
import time
import threading
import logging
from flask import Flask, jsonify
from openai import OpenAI
from collections import defaultdict

TOKEN = os.getenv("TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
CHANNEL = "@your_channel"

bot = telebot.TeleBot(TOKEN, threaded=True)
app = Flask(__name__)
client = OpenAI(api_key=OPENAI_KEY)

logging.basicConfig(level=logging.INFO)

# ================= DB =================
conn = sqlite3.connect("final_god.db", check_same_thread=False)
cur = conn.cursor()
lock = threading.Lock()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
user_id INTEGER PRIMARY KEY,
coins INTEGER DEFAULT 10,
xp INTEGER DEFAULT 0,
level INTEGER DEFAULT 1,
vip INTEGER DEFAULT 0,
personality TEXT DEFAULT 'neutral'
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS memory (
user_id INTEGER,
text TEXT
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

conn.commit()

# ================= MEMORY =================
memory_cache = defaultdict(list)
last_time = defaultdict(float)
last_reply = defaultdict(str)

RATE = 2.5


def spam(uid):
    now = time.time()
    if now - last_time[uid] < RATE:
        return True
    last_time[uid] = now
    return False


def check_join(uid):
    try:
        m = bot.get_chat_member(CHANNEL, uid)
        return m.status in ["member", "administrator", "creator"]
    except:
        return False
        def get_personality(uid):
    with lock:
        cur.execute("SELECT personality FROM users WHERE user_id=?", (uid,))
        r = cur.fetchone()
    return r[0] if r else "neutral"


def system_prompt(uid):
    p = get_personality(uid)

    base = "You are a powerful Telegram AI assistant."

    if p == "funny":
        return base + " Be funny and creative."
    if p == "coder":
        return base + " Focus on coding and logic."
    if p == "serious":
        return base + " Be short and precise."

    return base + " Be natural and helpful."


def ai_reply(uid, text):
    try:
        history = memory_cache[uid][-6:]

        messages = [{"role": "system", "content": system_prompt(uid)}]

        for h in history:
            messages.append({"role": "user", "content": h})

        messages.append({"role": "user", "content": text})

        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        reply = res.choices[0].message.content

        # anti repetition
        if reply == last_reply[uid]:
            reply += "."

        last_reply[uid] = reply
        memory_cache[uid].append(text)

        if len(memory_cache[uid]) > 20:
            memory_cache[uid].pop(0)

        with lock:
            cur.execute("INSERT INTO memory VALUES (?,?)", (uid, text))
            conn.commit()

        return reply

    except Exception as e:
        logging.error(e)
        return "⚠️ AI error"
        def menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("💰 Coins", "📊 Level")
    kb.row("🛍 Store", "🛒 Buy")
    kb.row("🏪 Sell", "🤖 AI")
    kb.row("⚙ AI Mode", "👑 VIP")
    return kb


@bot.message_handler(commands=["start"])
def start(m):
    with lock:
        cur.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (m.from_user.id,))
        conn.commit()

    if not check_join(m.from_user.id):
        bot.send_message(m.chat.id, "❌ Join channel first: " + CHANNEL)
        return

    bot.send_message(m.chat.id, ai_reply(m.from_user.id, "welcome user"), reply_markup=menu())


# ================= COINS =================
@bot.message_handler(func=lambda m: m.text == "💰 Coins")
def coins(m):
    if spam(m.from_user.id): return
    c,x,l,v = get_user(m.from_user.id)
    bot.send_message(m.chat.id, f"💰 {c}")


# ================= LEVEL =================
@bot.message_handler(func=lambda m: m.text == "📊 Level")
def level(m):
    c,x,l,v = get_user(m.from_user.id)
    bot.send_message(m.chat.id, f"⭐ {l} | XP {x}")


# ================= STORE =================
@bot.message_handler(func=lambda m: m.text == "🛍 Store")
def store(m):
    with lock:
        cur.execute("SELECT * FROM products")
        rows = cur.fetchall()

    bot.send_message(m.chat.id, ai_reply(m.from_user.id, str(rows)))


# ================= SELL =================
@bot.message_handler(func=lambda m: m.text == "🏪 Sell")
def sell(m):
    msg = bot.send_message(m.chat.id, "title price")
    bot.register_next_step_handler(msg, save)

def save(m):
    try:
        t,p = m.text.split()
        with lock:
            cur.execute("INSERT INTO products VALUES (NULL,?,?,?)",
                        (m.from_user.id,t,int(p)))
            conn.commit()
        bot.send_message(m.chat.id, ai_reply(m.from_user.id, "added"))
    except:
        bot.send_message(m.chat.id, "error")


# ================= BUY =================
@bot.message_handler(func=lambda m: m.text == "🛒 Buy")
def buy(m):
    with lock:
        cur.execute("SELECT * FROM products")
        rows = cur.fetchall()

    bot.send_message(m.chat.id, ai_reply(m.from_user.id, str(rows)))


# ================= AI CHAT =================
@bot.message_handler(func=lambda m: m.text == "🤖 AI")
def ai(m):
    msg = bot.send_message(m.chat.id, "Ask anything:")
    bot.register_next_step_handler(msg, step)

def step(m):
    if spam(m.from_user.id): return
    bot.send_message(m.chat.id, ai_reply(m.from_user.id, m.text))


# ================= AI MODE =================
@bot.message_handler(func=lambda m: m.text == "⚙ AI Mode")
def mode(m):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("funny","serious","coder","neutral")
    bot.send_message(m.chat.id, "Choose mode", reply_markup=kb)


@bot.message_handler(func=lambda m: m.text in ["funny","serious","coder","neutral"])
def set_mode(m):
    with lock:
        cur.execute("UPDATE users SET personality=? WHERE user_id=?",
                    (m.text,m.from_user.id))
        conn.commit()
    bot.send_message(m.chat.id, ai_reply(m.from_user.id, "mode changed"))


# ================= VIP =================
@bot.message_handler(func=lambda m: m.text == "👑 VIP")
def vip(m):
    c,x,l,v = get_user(m.from_user.id)
    bot.send_message(m.chat.id, "VIP ACTIVE" if v else "NO VIP")


# ================= FLASK =================
@app.route("/")
def home():
    return jsonify({"status":"FINAL GOD MODE ACTIVE"})

@app.route("/stats")
def stats():
    with lock:
        cur.execute("SELECT COUNT(*) FROM users")
        u = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM products")
        p = cur.fetchone()[0]

    return jsonify({"users":u,"products":p})


# ================= RUN =================
def run_bot():
    while True:
        try:
            bot.infinity_polling()
        except Exception as e:
            logging.error(e)
            time.sleep(3)


def run_web():
    app.run(host="0.0.0.0", port=5000)


threading.Thread(target=run_bot).start()
threading.Thread(target=run_web).start()
