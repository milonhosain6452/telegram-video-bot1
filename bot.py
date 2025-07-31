import os
import json
import string
import random
from flask import Flask, render_template, redirect, url_for
from threading import Thread
from pyrogram import Client, filters
from pyrogram.types import Message

# -------------------------------
# 🔐 Bot Configuration
API_ID = 18088290
API_HASH = "1b06cbb45d19188307f10bcf275341c5"
BOT_TOKEN = "8022559940:AAHNNdMOfp4af6dI6rT21YP4phDSv-K8giQ"
REDIRECT_DOMAIN = "https://teraboxlink.free.nf/redirect.html?url="  # আপনার হোস্টিং URL
# -------------------------------

# ✅ Flask App
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Link shortener is running!"

# ✅ JSON DB init
if not os.path.exists("data.json"):
    with open("data.json", "w") as f:
        json.dump({"links": {}}, f)

# ✅ Pyrogram Bot
bot = Client("shortlink-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def save_link(code, url):
    with open("data.json", "r") as f:
        data = json.load(f)
    data["links"][code] = url
    with open("data.json", "w") as f:
        json.dump(data, f)

@bot.on_message(filters.command("start") & filters.private)
async def start_handler(_, message: Message):
    await message.reply("""
🌟 Welcome to URL Shortener Bot!
Send /short <your_url> to create a short link.
Example: /short https://example.com
""")

@bot.on_message(filters.command("short") & filters.private)
async def short_link_handler(_, message: Message):
    if len(message.command) < 2:
        return await message.reply("Usage: /short <URL>")

    url = message.text.split(None, 1)[1]
    code = generate_code()
    save_link(code, url)
    
    # Redirect through your hosting with the actual URL as parameter
    redirect_url = f"{REDIRECT_DOMAIN}{url}"
    short_url = f"https://teraboxlink.free.nf/{code}"  # This is just for show
    
    await message.reply(f"""
✅ Your short link created!
🔗 Short URL: {short_url}
📌 Original URL: {url}

Note: Users will see ads before redirecting.
""")

# ✅ Run Flask in a thread
def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# ✅ Start both Flask and bot
if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.run()
