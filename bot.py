import telebot
from telebot import types
import sqlite3
import os
import time
import threading
from flask import Flask, jsonify
from openai import OpenAI
from collections import defaultdict

TOKEN = os.getenv("TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

CHANNEL = "@your_channel"

bot = telebot.TeleBot(TOKEN, threaded=True)
app = Flask(__name__)
client = OpenAI(api_key=OPENAI_API_KEY)

conn = sqlite3.connect("final_locked.db", check_same_thread=False)
cur = conn.cursor()
lock = threading.Lock()

# ================= DATABASE =================
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
user_id INTEGER PRIMARY KEY,
coins INTEGER DEFAULT 20,
xp INTEGER DEFAULT 0,
level INTEGER DEFAULT 1,
vip TEXT DEFAULT 'none',
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
RATE = 2.5


def spam(uid):
    now = time.time()
    if now - last_time[uid] < RATE:
        return True
    last_time[uid] = now
    return False


# ================= FORCE JOIN =================
def check_join(uid):
    try:
        m = bot.get_chat_member(CHANNEL, uid)
        return m.status in ["member", "administrator", "creator"]
    except:
        return False
        # ================= USER =================
def get_user(uid):
    with lock:
        cur.execute("SELECT coins,xp,level,vip FROM users WHERE user_id=?", (uid,))
        return cur.fetchone() or (20,0,1,"none")


def ensure_user(uid):
    with lock:
        cur.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (uid,))
        conn.commit()


# ================= VIP DISCOUNT =================
def discount(uid):
    _,_,_,vip = get_user(uid)
    if vip == "vip":
        return 0.85
    if vip == "vip_pro":
        return 0.70
    return 1


# ================= MEMORY =================
def save_memory(uid, text):
    with lock:
        cur.execute("INSERT INTO memory VALUES (?,?)", (uid, text))
        conn.commit()


def load_memory(uid):
    with lock:
        cur.execute("SELECT text FROM memory WHERE user_id=? ORDER BY rowid DESC LIMIT 10", (uid,))
        return [x[0] for x in cur.fetchall()][::-1]


# ================= AI ENGINE (NO STATIC MESSAGE MODE) =================
def ai(uid, text):

    history = memory_cache[uid][-6:]
    db_mem = load_memory(uid)

    messages = [
        {
            "role": "system",
            "content": "You are an advanced Telegram AI agent. Never give suggestions unless asked. Never mention upgrades. Never output static templates."
        }
    ]

    for m in db_mem:
        messages.append({"role": "user", "content": m})

    for h in history:
        messages.append({"role": "user", "content": h})

    messages.append({"role": "user", "content": text})

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    reply = res.choices[0].message.content

    memory_cache[uid].append(text)
    save_memory(uid, text)

    return reply


# ================= AGENT (NO SUGGESTION MODE) =================
def agent(uid, text):

    user = get_user(uid)
    coins = user[0]

    if coins < 5:
        return ai(uid, "User low coins state detected. respond only to request, no suggestions.")

    if "buy" in text.lower():
        return ai(uid, "User buying intent detected. respond only directly.")

    if "code" in text.lower():
        return ai(uid, "Coding request detected. respond with solution only.")

    return ai(uid, text)
    # ================= BUY SYSTEM =================
def buy_item(uid, item_id):
    with lock:
        cur.execute("SELECT price FROM products WHERE id=?", (item_id,))
        item = cur.fetchone()

        if not item:
            return "NO_DATA"

        price = int(item[0] * discount(uid))

        cur.execute("SELECT coins FROM users WHERE user_id=?", (uid,))
        coins = cur.fetchone()[0]

        if coins < price:
            return "INSUFFICIENT_FUNDS"

        cur.execute("UPDATE users SET coins=coins-? WHERE user_id=?", (price, uid))
        conn.commit()

        return f"OK:{price}"


# ================= BOT =================
@bot.message_handler(commands=["start"])
def start(m):

    ensure_user(m.from_user.id)

    if not check_join(m.from_user.id):
        bot.send_message(m.chat.id, "ACCESS_DENIED")
        return

    bot.send_message(m.chat.id, ai(m.from_user.id, "user joined bot"))


@bot.message_handler(func=lambda m: m.text == "🛒 Buy")
def buy(m):
    with lock:
        cur.execute("SELECT * FROM products")
        rows = cur.fetchall()

    bot.send_message(m.chat.id, ai(m.from_user.id, str(rows)))


@bot.message_handler(func=lambda m: m.text.startswith("buy "))
def buy_cmd(m):
    item_id = int(m.text.split()[1])
    bot.send_message(m.chat.id, buy_item(m.from_user.id, item_id))


@bot.message_handler(func=lambda m: True)
def all_messages(m):

    if spam(m.from_user.id):
        return

    # FINAL RULE: NO STATIC OUTPUTS EVER
    bot.send_message(m.chat.id, agent(m.from_user.id, m.text))


# ================= FLASK DASHBOARD =================
@app.route("/")
def home():
    return jsonify({"status": "FINAL LOCKED AI ACTIVE"})


@app.route("/stats")
def stats():
    with lock:
        cur.execute("SELECT COUNT(*) FROM users")
        u = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM products")
        p = cur.fetchone()[0]

    return jsonify({"users": u, "products": p})


# ================= RUN =================
def run_bot():
    bot.infinity_polling()

def run_web():
    app.run(host="0.0.0.0", port=5000)


threading.Thread(target=run_bot).start()
threading.Thread(target=run_web).start()
