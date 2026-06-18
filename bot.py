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
CHANNEL = "@config_v2ray_mpt"

bot = telebot.TeleBot(TOKEN, threaded=True)
app = Flask(__name__)
client = OpenAI(api_key=OPENAI_API_KEY)

# ================= DB =================
conn = sqlite3.connect("god_ultra.db", check_same_thread=False)
cur = conn.cursor()
lock = threading.Lock()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
user_id INTEGER PRIMARY KEY,
coins INTEGER DEFAULT 20,
xp INTEGER DEFAULT 0,
level INTEGER DEFAULT 1,
vip TEXT DEFAULT 'none',
personality TEXT DEFAULT 'neutral',
summary TEXT DEFAULT ''
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS memory (
user_id INTEGER,
text TEXT,
ts REAL
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


def save_memory(uid, text):
    with lock:
        cur.execute("INSERT INTO memory VALUES (?,?,?)", (uid, text, time.time()))
        conn.commit()


def load_memory(uid):
    with lock:
        cur.execute("SELECT text FROM memory WHERE user_id=? ORDER BY ts DESC LIMIT 10", (uid,))
        return [x[0] for x in cur.fetchall()][::-1]


def update_summary(uid, text):
    with lock:
        cur.execute("SELECT summary FROM users WHERE user_id=?", (uid,))
        old = cur.fetchone()
        old = old[0] if old and old[0] else ""

        new_sum = (old + " " + text)[-1200:]

        cur.execute("UPDATE users SET summary=? WHERE user_id=?",
                    (new_sum, uid))
        conn.commit()
        def ensure_user(uid):
    with lock:
        cur.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (uid,))
        conn.commit()


def get_user(uid):
    with lock:
        cur.execute("""
        SELECT coins,xp,level,vip,personality,summary
        FROM users WHERE user_id=?
        """, (uid,))
        return cur.fetchone() or (20,0,1,"none","neutral","")


def vip_discount(vip):
    if vip == "vip":
        return 0.85
    if vip == "vip_pro":
        return 0.70
    return 1


# ================= PERSONALITY =================
def system_prompt(p):
    base = "You are a powerful Telegram AI assistant."

    if p == "funny":
        return base + " Be funny and sarcastic."
    if p == "serious":
        return base + " Be direct and professional."
    if p == "coder":
        return base + " Focus on programming solutions."

    return base


# ================= AI ENGINE =================
def ai(uid, text):
    coins, xp, lvl, vip, personality, summary = get_user(uid)

    history = memory_cache[uid][-6:]
    db_mem = load_memory(uid)

    messages = [
        {"role": "system", "content": system_prompt(personality)},
        {"role": "system", "content": f"Memory summary: {summary}"}
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

    if reply == last_reply[uid]:
        reply += "."

    last_reply[uid] = reply
    memory_cache[uid].append(text)

    save_memory(uid, text)
    update_summary(uid, text)

    return reply


# ================= AGENT SYSTEM =================
def agent(uid, text):
    coins, xp, lvl, vip, personality, summary = get_user(uid)

    if coins < 5:
        return ai(uid, "low balance mode: answer only")

    if "buy" in text.lower():
        return ai(uid, "purchase intent detected")

    if "code" in text.lower():
        return ai(uid, "coding request detected")

    return ai(uid, text)
    # ================= FORCE JOIN =================
def check_join(uid):
    try:
        m = bot.get_chat_member(CHANNEL, uid)
        return m.status in ["member","administrator","creator"]
    except:
        return False


# ================= BUY SYSTEM =================
def buy_item(uid, item_id):
    with lock:
        cur.execute("SELECT price FROM products WHERE id=?", (item_id,))
        item = cur.fetchone()

        if not item:
            return "NOT_FOUND"

        price = item[0]

        cur.execute("SELECT coins FROM users WHERE user_id=?", (uid,))
        coins = cur.fetchone()[0]

        if coins < price:
            return "NO_MONEY"

        cur.execute("UPDATE users SET coins=coins-? WHERE user_id=?", (price, uid))
        conn.commit()

        return f"OK:{price}"


# ================= START =================
@bot.message_handler(commands=["start"])
def start(m):
    ensure_user(m.from_user.id)

    if not check_join(m.from_user.id):
        bot.send_message(m.chat.id, ai(m.from_user.id, "user must join channel"))
        return

    bot.send_message(m.chat.id, ai(m.from_user.id, "welcome user"))


# ================= CHAT =================
@bot.message_handler(func=lambda m: True)
def all_messages(m):
    if spam(m.from_user.id):
        return

    bot.send_message(m.chat.id, agent(m.from_user.id, m.text))


# ================= FLASK =================
@app.route("/")
def home():
    return jsonify({"status":"GOD ULTRA ACTIVE"})


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
    bot.infinity_polling()

def run_web():
    app.run(host="0.0.0.0", port=5000)


threading.Thread(target=run_bot).start()
threading.Thread(target=run_web).start()
