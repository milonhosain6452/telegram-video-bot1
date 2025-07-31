import os
import json
import string
import random
import mysql.connector
from flask import Flask
from threading import Thread
from pyrogram import Client, filters
from pyrogram.types import Message

# -------------------------------
# 🔐 Bot Configuration
API_ID = 18088290
API_HASH = "1b06cbb45d19188307f10bcf275341c5"
BOT_TOKEN = "8022559940:AAHNNdMOfp4af6dI6rT21YP4phDSv-K8giQ"
BASE_URL = "https://shortlinks.wuaze.com/"  # আপনার হোস্টিং URL
# -------------------------------

# ✅ Database Configuration (InfinityFree)
DB_CONFIG = {
    'host': 'sql103.infinityfree.com',  # আপনার হোস্টনেম (cPanel MySQL Section এ পাবেন)
    'user': 'if0_39544523',  # আপনার InfinityFree MySQL ইউজারনেম
    'password': 'LZMARd0bFbNbcAd',  # আপনার সেট করা পাসওয়ার্ড
    'database': 'if0_39544523_teraboxshort_db'  # আপনার ডাটাবেস নাম
}

# ✅ Flask App
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Link shortener is running!"

# ✅ Initialize Database Connection
def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

# ✅ Initialize Database Table
def init_db():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS links (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    code VARCHAR(10) UNIQUE NOT NULL,
                    original_url TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            print("Database table initialized successfully")
        except mysql.connector.Error as err:
            print(f"Error initializing database: {err}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

# ✅ JSON DB backup (optional)
if not os.path.exists("data.json"):
    with open("data.json", "w") as f:
        json.dump({"links": {}}, f)

# ✅ Pyrogram Bot
bot = Client("shortlink-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def save_link(code, url):
    # Save to MySQL database
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            sql = "INSERT INTO links (code, original_url) VALUES (%s, %s)"
            val = (code, url)
            cursor.execute(sql, val)
            conn.commit()
            print(f"Link saved to database: {code} => {url}")
        except mysql.connector.Error as err:
            print(f"Error saving to database: {err}")
            # Fallback to JSON if database fails
            with open("data.json", "r") as f:
                data = json.load(f)
            data["links"][code] = url
            with open("data.json", "w") as f:
                json.dump(data, f)
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    else:
        # Fallback to JSON if no connection
        with open("data.json", "r") as f:
            data = json.load(f)
        data["links"][code] = url
        with open("data.json", "w") as f:
            json.dump(data, f)

@bot.on_message(filters.command("start") & filters.private)
async def start_handler(_, message: Message):
    await message.reply(f"""
🌟 Welcome to URL Shortener Bot!
Send /short <your_url> to create a short link.
Example: /short https://example.com

🔗 Your links will redirect through: {BASE_URL}
""")

@bot.on_message(filters.command("short") & filters.private)
async def short_link_handler(_, message: Message):
    if len(message.command) < 2:
        return await message.reply("Usage: /short <URL>")

    url = message.text.split(None, 1)[1]
    
    # Validate URL format
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    code = generate_code()
    save_link(code, url)
    
    short_url = f"{BASE_URL}{code}"
    
    await message.reply(f"""
✅ Your short link created!
🔗 Short URL: {short_url}
📌 Original URL: {url}

Note: Users will see ads before redirecting to the original URL.
""")

# ✅ Run Flask in a thread
def run_flask():
    # Initialize database on startup
    init_db()
    
    port = int(os.environ.get("PORT", 10000))  # Render.com uses PORT env var
    app.run(host="0.0.0.0", port=port)

# ✅ Start both Flask and bot
if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.run()
