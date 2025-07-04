import os
import sqlite3
import threading
import time
from pyrogram import Client, filters
from flask import Flask

# --- Credentials ---
API_ID = 18088290
API_HASH = "1b06cbb45d19188307f10bcf275341c5"
BOT_TOKEN = "8154600064:AAF5wHjPAnCUYII2Fp3XleRTtUMcUzr2M9g"
CHANNEL_ID = -1002899840201
BOT_USERNAME = "video12321_bot"  # ✅ তোমার বটের ইউজারনেম

# --- Setup ---
bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
app = Flask(__name__)

# --- Database ---
def init_db():
    with sqlite3.connect("database.db") as db:
        db.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
        db.execute("CREATE TABLE IF NOT EXISTS links (code TEXT PRIMARY KEY, message_id INTEGER)")
init_db()

# --- Auto Delete After 30 Minutes ---
def auto_delete(chat_id, msg_id):
    time.sleep(1800)
    try:
        bot.delete_messages(chat_id, msg_id)
    except Exception as e:
        print(f"[Delete Error] {e}")

# --- /start Handler ---
@bot.on_message(filters.command("start") & filters.private)
def start_handler(client, message):
    user_id = message.from_user.id
    with sqlite3.connect("database.db") as db:
        db.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    
    if len(message.command) > 1:
        payload = message.command[1]
        if payload.startswith("video"):
            try:
                msg_id = int(payload.replace("video", ""))
                with sqlite3.connect("database.db") as db:
                    db.execute("INSERT OR IGNORE INTO links (code, message_id) VALUES (?, ?)", (payload, msg_id))
                sent = bot.send_video(chat_id=user_id, from_chat_id=CHANNEL_ID, message_id=msg_id)
                threading.Thread(target=auto_delete, args=(user_id, sent.id)).start()
            except Exception as e:
                print(e)
                message.reply_text("❌ ভিডিও আনতে সমস্যা হচ্ছে।")
        else:
            message.reply_text("👋 হ্যালো! আপনি রেজিস্টার্ড।")
    else:
        message.reply_text("👋 Send /genlink <channel video link> to get a private link.")

# --- /genlink Handler ---
@bot.on_message(filters.command("genlink") & filters.private)
def genlink_handler(client, message):
    user_id = message.from_user.id
    if len(message.command) < 2:
        return message.reply_text("❗ Usage: /genlink <channel post link>")
    
    try:
        link = message.command[1]
        msg_id = int(link.split("/")[-1])
        code = f"video{msg_id}"
        
        with sqlite3.connect("database.db") as db:
            db.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
            db.execute("INSERT OR IGNORE INTO links (code, message_id) VALUES (?, ?)", (code, msg_id))
        
        deep_link = f"https://t.me/{BOT_USERNAME}?start={code}"
        message.reply_text(f"✅ Your private video link:\n{deep_link}")
    
    except Exception as e:
        print(e)
        message.reply_text("❌ Invalid video link.")

# --- Optional Flask route for UptimeRobot (Render ping) ---
@app.route("/")
def home():
    return "✅ Bot is Live"

# --- Run Both Flask & Bot ---
def run_flask():
    app.run(host="0.0.0.0", port=8080)

def run_bot():
    bot.run()

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    run_bot()
