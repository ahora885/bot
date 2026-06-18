import telebot
from telebot import types
import sqlite3
import os
import time
import threading
from flask import Flask, jsonify
from openai import OpenAI
from collections import defaultdict
import numpy as np

TOKEN = os.getenv("TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

CHANNEL = "@your_channel"

bot = telebot.TeleBot(TOKEN, threaded=True, skip_pending=True)
app = Flask(__name__)
client = OpenAI(api_key=OPENAI_API_KEY)

conn = sqlite3.connect("ultimate_ai.db", check_same_thread=False)
cur = conn.cursor()
lock = threading.Lock()

# ================= DB =================
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
user_id INTEGER PRIMARY KEY,
coins INTEGER DEFAULT 20,
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
title TEXT,
price INTEGER
)
""")

conn.commit()

# ================= MEMORY CACHE =================
memory_cache = defaultdict(list)

# ================= FAISS SIMPLE VECTOR MEMORY =================
vector_memory = defaultdict(list)

def embed(text):
    res = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return np.array(res.data[0].embedding)


def save_vector(uid, text):
    vector_memory[uid].append((text, embed(text)))


def search_memory(uid, query, top_k=3):
    if uid not in vector_memory:
        return []

    q_vec = embed(query)
    scored = []

    for text, vec in vector_memory[uid]:
        score = np.dot(q_vec, vec)
        scored.append((score, text))

    scored.sort(reverse=True)
    return [t for _, t in scored[:top_k]]
    def tools():
    return {
        "store": get_store,
        "buy": buy_item,
        "memory": get_memory
    }


def get_store(uid):
    with lock:
        cur.execute("SELECT * FROM products")
        return cur.fetchall()


def get_memory(uid, query):
    return search_memory(uid, query)


# ================= REASONING LOOP =================
def reasoning(uid, text):

    step1 = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Decide action: store / memory / chat / buy"},
            {"role": "user", "content": text}
        ]
    ).choices[0].message.content.lower()

    if "store" in step1:
        return str(get_store(uid))

    if "memory" in step1:
        return str(get_memory(uid, text))

    return chat(uid, text)


# ================= MAIN CHAT =================
def chat(uid, text):

    mem = memory_cache[uid][-6:]

    context = search_memory(uid, text)

    messages = [
        {"role": "system", "content": "You are a smart AI agent."}
    ]

    for c in context:
        messages.append({"role": "user", "content": c})

    for m in mem:
        messages.append({"role": "user", "content": m})

    messages.append({"role": "user", "content": text})

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    reply = res.choices[0].message.content

    memory_cache[uid].append(text)
    save_vector(uid, text)

    return reply
    def ensure_user(uid):
    with lock:
        cur.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (uid,))
        conn.commit()


def get_user(uid):
    with lock:
        cur.execute("SELECT coins,vip FROM users WHERE user_id=?", (uid,))
        return cur.fetchone() or (20, "none")


def discount(uid):
    _, vip = get_user(uid)
    if vip == "vip":
        return 0.8
    if vip == "vip_pro":
        return 0.6
    return 1


def buy_item(uid, item_id):
    with lock:
        cur.execute("SELECT price FROM products WHERE id=?", (item_id,))
        item = cur.fetchone()
        if not item:
            return "NO_ITEM"

        price = int(item[0] * discount(uid))

        cur.execute("SELECT coins FROM users WHERE user_id=?", (uid,))
        coins = cur.fetchone()[0]

        if coins < price:
            return "NO_MONEY"

        cur.execute("UPDATE users SET coins=coins-? WHERE user_id=?", (price, uid))
        conn.commit()

        return f"OK {price}"


# ================= GOAL AGENT =================
def goal_agent(uid, text):
    plan = reasoning(uid, text)
    return plan


# ================= BOT =================
@bot.message_handler(commands=["start"])
def start(m):

    uid = m.from_user.id
    ensure_user(uid)

    if CHANNEL and not bot.get_chat_member(CHANNEL, uid).status in ["member", "administrator", "creator"]:
        bot.send_message(m.chat.id, "ACCESS REQUIRED")
        return

    bot.send_message(m.chat.id, goal_agent(uid, "welcome user"))


@bot.message_handler(func=lambda m: True)
def all_msg(m):

    uid = m.from_user.id

    bot.send_message(
        m.chat.id,
        goal_agent(uid, m.text)
    )


# ================= FLASK =================
@app.route("/")
def home():
    return jsonify({"status": "V3 ULTIMATE AI ACTIVE"})


# ================= RUN =================
def run_bot():
    bot.infinity_polling()

def run_web():
    app.run(host="0.0.0.0", port=5000)


threading.Thread(target=run_bot).start()
threading.Thread(target=run_web).start()
