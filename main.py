import os
import json
import re
from datetime import datetime
from threading import Thread
from flask import Flask, render_template, send_from_directory
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

DATA_FILE = "messages.json"
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def safe_filename(filename):
    # Fayl nomidan maxsus belgilarni olib tashlaydi
    return re.sub(r"[^a-zA-Z0-9_.-]", "_", filename)


def save_message(data):
    messages = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            messages = json.load(f)
    messages.append(data)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)
    print(f"✅ Message saved: {data}")


app = Flask(__name__)


@app.route("/")
def index():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            messages = json.load(f)
    else:
        messages = []
    return render_template("index.html", messages=messages)


@app.route("/downloads/<path:filename>")
def download_file(filename):
    return send_from_directory(DOWNLOAD_DIR, filename)


def run_flask():
    print("✅ Flask API ishlayapti: http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)


# Bu yerga haqiqiy Telegram bot tokeningizni qo'ying
TOKEN = (
    "7882445134:AAH5YvMglKDH11PbTMSsYTomsxtwZSWJHHk"  # yoki sizning haqiqiy tokeningiz
)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = {
        "user": user.full_name,
        "time": timestamp,
        "type": "text",
        "content": update.message.text,
    }
    save_message(msg)


async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    document = update.message.document
    file = await document.get_file()

    filename = safe_filename(document.file_name)
    file_path = os.path.join(DOWNLOAD_DIR, filename)

    print(f"📁 Yuklanmoqda: {filename} -> {file_path}")
    await file.download_to_drive(file_path)
    print("✅ Yuklash tugadi")

    msg = {
        "user": user.full_name,
        "time": timestamp,
        "type": "file",
        "content": f"/downloads/{filename}",
    }
    save_message(msg)


if __name__ == "__main__":
    # Flask serverini alohida ipda ishga tushiramiz
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Telegram botni ishga tushiramiz
    application = Application.builder().token(TOKEN).build()
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    print("✅ Telegram bot ishga tushdi...")
    application.run_polling()
