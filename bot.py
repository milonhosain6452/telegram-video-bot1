import os
import sqlite3
import string
import random
import threading
import time
from flask import Flask, request
from pyrogram import Client, filters

# Credentials
API_ID = 18088290
API_HASH = "1b06cbb45d19188307f10bcf275341c5"
BOT_TOKEN = "8154600064:AAF5wHjPAnCUYII2Fp3XleRTtUMcUzr2M9g"
CHANNEL_ID = -1002899840201

# Setup Bot & Flask
bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
app = Flask(__name__)

# --- DB SETUP ---
def init_db():
    conn = sqlite3.connect("database.db")
    conn.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
    conn.execute("CREATE TABLE IF NOT EXISTS links (code TEXT, message_id INTEGER, user_id INTEGER)")
    conn.commit()
    conn.close()

init_db()

# --- HELPERS ---
def generate_code(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# --- BOT HANDLERS ---
@bot.on_message(filters.command("start") & filters.private)
def start(client, message):
    user_id = message.from_user.id
    with sqlite3.connect("database.db") as db:
        db.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    message.reply_text("✅ You're registered! Use /genlink <channel_link> to get a sharable link.")

@bot.on_message(filters.command("genlink") & filters.private)
def genlink(client, message):
    user_id = message.from_user.id
    if len(message.command) < 2:
        return message.reply_text("❗ Send like this: /genlink <channel link>")
    link = message.command[1]
    try:
        message_id = int(link.split("/")[-1])
        code = generate_code()
        with sqlite3.connect("database.db") as db:
            db.execute("INSERT INTO links (code, message_id, user_id) VALUES (?, ?, ?)", (code, message_id, user_id))
        domain = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "localhost:8080")
        link_url = f"https://{domain}/{code}"
        message.reply_text(f"✅ Your private video link:\n{link_url}")
    except Exception as e:
        message.reply_text("❌ Invalid link. Try again.")
        print(e)

# --- FLASK ROUTE ---
@app.route("/")
def home():
    return "✅ Bot is Live."

@app.route("/<code>")
def serve_video(code):
    with sqlite3.connect("database.db") as db:
        result = db.execute("SELECT message_id, user_id FROM links WHERE code = ?", (code,)).fetchone()
    if result:
        msg_id, user_id = result
        try:
            sent = bot.send_video(chat_id=user_id, from_chat_id=CHANNEL_ID, message_id=msg_id)
            threading.Thread(target=auto_delete, args=(user_id, sent.id)).start()
            return "📤 Video sent to your Telegram!"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    else:
        return "❌ Invalid or expired link."

def auto_delete(chat_id, msg_id):
    time.sleep(1800)  # 30 minutes
    try:
        bot.delete_messages(chat_id, msg_id)
    except Exception as e:
        print(f"[delete error] {e}")

# --- RUN ---
def run_flask():
    app.run(host="0.0.0.0", port=8080)

def run_bot():
    bot.run()

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    run_bot()
