import os
import sqlite3
import threading
import time
from flask import Flask
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
    conn.execute("CREATE TABLE IF NOT EXISTS links (code TEXT PRIMARY KEY, message_id INTEGER)")
    conn.commit()
    conn.close()

init_db()

# --- AUTO DELETE FUNCTION ---
def auto_delete(chat_id, msg_id):
    time.sleep(1800)  # 30 minutes
    try:
        bot.delete_messages(chat_id, msg_id)
    except Exception as e:
        print(f"[delete error] {e}")

# --- /start HANDLER ---
@bot.on_message(filters.command("start") & filters.private)
def start(client, message):
    user_id = message.from_user.id
    with sqlite3.connect("database.db") as db:
        db.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    if len(message.command) > 1:
        payload = message.command[1]
        if payload.startswith("vid"):
            try:
                message_id = int(payload[3:])
                with sqlite3.connect("database.db") as db:
                    db.execute("INSERT OR IGNORE INTO links (code, message_id) VALUES (?, ?)", (payload, message_id))
                sent = bot.send_video(chat_id=user_id, from_chat_id=CHANNEL_ID, message_id=message_id)
                threading.Thread(target=auto_delete, args=(user_id, sent.id)).start()
            except Exception as e:
                print(f"[error] {e}")
                message.reply_text("❌ Couldn't fetch the video.")
        else:
            message.reply_text("👋 Welcome to the bot!")
    else:
        message.reply_text("👋 You're registered!\nSend /genlink <channel link> to get a private link.")

# --- /genlink HANDLER ---
@bot.on_message(filters.command("genlink") & filters.private)
def genlink(client, message):
    user_id = message.from_user.id
    if len(message.command) < 2:
        return message.reply_text("❗ Send like this: /genlink <channel link>")
    link = message.command[1]
    try:
        message_id = int(link.split("/")[-1])
        code = f"vid{message_id}"
        with sqlite3.connect("database.db") as db:
            db.execute("INSERT OR IGNORE INTO links (code, message_id) VALUES (?, ?)", (code, message_id))
            db.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        deep_link = f"https://t.me/YourVideoss_bot?start={code}"
        message.reply_text(f"✅ Your private video link:\n{deep_link}")
    except Exception as e:
        message.reply_text("❌ Invalid link format.")
        print(e)

# --- FLASK (Optional for Render Uptime Ping) ---
@app.route("/")
def home():
    return "✅ Bot is Live."

# --- RUN ---
def run_flask():
    app.run(host="0.0.0.0", port=8080)

def run_bot():
    bot.run()

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    run_bot()
