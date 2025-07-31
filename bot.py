import json
import string
import random
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = 18088290
API_HASH = "1b06cbb45d19188307f10bcf275341c5"
BOT_TOKEN = "7628770960:AAEIwuSGBWjFttb-9Aanm68JNnzEY3PuWlo"
BASE_URL = "https://yourappname.onrender.com/"  # ✅ আপনার Render URL বসান এখানে

app = Client("shortlink-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def save_link(code, url):
    with open("data.json", "r") as f:
        data = json.load(f)
    data["links"][code] = url
    with open("data.json", "w") as f:
        json.dump(data, f)

@app.on_message(filters.command("short") & filters.private)
async def short_link(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("Usage: /short <url>", quote=True)

    original_url = message.text.split(None, 1)[1]
    code = generate_code()
    save_link(code, original_url)
    short_url = f"{BASE_URL}{code}"
    await message.reply(f"✅ Here is your short link:\n\n{short_url}", quote=True)

app.run()
