import os
import time
import sqlite3
import threading
import numpy as np
import faiss
import telebot
from flask import Flask, jsonify
from openai import OpenAI
from collections import defaultdict

# ================= CONFIG =================
TOKEN = os.getenv("TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(TOKEN, skip_pending=True)
app = Flask(__name__)
client = OpenAI(api_key=OPENAI_API_KEY)

lock = threading.Lock()

# ================= DATABASE =================
conn = sqlite3.connect("ultimate_ai.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS memory (
user_id INTEGER,
text TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS plugins (
name TEXT,
code TEXT
)
""")

conn.commit()

# ================= FAISS MEMORY =================
DIM = 1536
index = faiss.IndexFlatL2(DIM)
vectors = []
meta = []

def embed(text):
    return np.array(
        client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        ).data[0].embedding,
        dtype=np.float32
    )

def add_memory(uid, text):
    vec = embed(text)
    index.add(np.array([vec]))
    vectors.append(vec)
    meta.append((uid, text))

# ================= MEMORY =================
memory_cache = defaultdict(list)

def load_memory(uid):
    cur.execute("SELECT text FROM memory WHERE user_id=? ORDER BY rowid DESC LIMIT 10", (uid,))
    return [x[0] for x in cur.fetchall()][::-1]

def save_memory(uid, text):
    with lock:
        cur.execute("INSERT INTO memory VALUES (?,?)", (uid, text))
        conn.commit()

# ================= PLUGIN SYSTEM =================
plugins = {}

def register(name):
    def wrapper(func):
        plugins[name] = func
        return func
    return wrapper

@register("time")
def plugin_time(uid, text):
    return time.ctime()

@register("echo")
def plugin_echo(uid, text):
    return f"ECHO: {text}"

# ================= SWARM (REALISTIC SIMULATION) =================
def swarm(uid, text):
    agents = {
        "analyzer": lambda t: f"[ANALYZE] {t}",
        "planner": lambda t: f"[PLAN] {t}",
        "executor": lambda t: f"[EXEC] {t}"
    }

    results = []
    for a in agents.values():
        results.append(a(text))

    return "\n".join(results)

# ================= RAG =================
def rag(uid, text):
    context = []

    if len(meta) > 0:
        q = embed(text).reshape(1, -1)
        _, I = index.search(q, 5)
        context = [meta[i][1] for i in I[0] if i < len(meta)]

    messages = [
        {"role": "system", "content": "Unified AI System (RAG + Agent + Swarm)"}
    ]

    for c in context:
        messages.append({"role": "user", "content": c})

    messages.append({"role": "user", "content": text})

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    return res.choices[0].message.content

# ================= AGENT ROUTER =================
def router(uid, text):

    if text.startswith("/plugin"):
        parts = text.split()
        name = parts[1] if len(parts) > 1 else ""
        return plugins.get(name, lambda u, t: "PLUGIN_NOT_FOUND")(uid, text)

    if "swarm" in text.lower():
        return swarm(uid, text)

    if "memory" in text.lower():
        return str(load_memory(uid))

    return rag(uid, text)

# ================= SELF-IMPROVE (SIMULATION ONLY) =================
def self_improve(text):
    return text + "\n\n[SELF-IMPROVE: optimized reasoning path applied]"

# ================= TELEGRAM =================
@bot.message_handler(commands=["start"])
def start(m):
    bot.send_message(m.chat.id, "ULTIMATE AI SYSTEM ACTIVE")

@bot.message_handler(func=lambda m: True)
def handle(m):

    uid = m.from_user.id
    text = m.text

    memory_cache[uid].append(text)
    save_memory(uid, text)
    add_memory(uid, text)

    response = router(uid, text)
    response = self_improve(response)

    bot.send_message(m.chat.id, response)

# ================= FLASK =================
@app.route("/")
def home():
    return jsonify({"status": "ULTIMATE AI RUNNING"})

@app.route("/stats")
def stats():
    return jsonify({
        "memory": len(meta),
        "users": len(memory_cache)
    })

# ================= RUN =================
def run_bot():
    bot.infinity_polling()

def run_web():
    app.run(host="0.0.0.0", port=5000)

threading.Thread(target=run_bot).start()
threading.Thread(target=run_web).start()
