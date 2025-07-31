import json
import os
from flask import Flask, render_template, redirect

app = Flask(__name__)

@app.route("/")
def index():
    return "✅ Link shortener is running!"

@app.route("/<code>")
def redirect_page(code):
    with open("data.json", "r") as f:
        data = json.load(f)

    if code in data["links"]:
        long_url = data["links"][code]
        return render_template("redirect.html", long_url=long_url)
    else:
        return "Invalid or expired link.", 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render থেকে PORT নিবে
    app.run(host="0.0.0.0", port=port)
