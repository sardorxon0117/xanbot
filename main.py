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

ADMIN_ID = 8040261812  # Admin user ID qo'shildi

def safe_filename(filename):
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

TOKEN = "7882445134:AAH5YvMglKDH11PbTMSsYTomsxtwZSWJHHk"

# --- Telegram handlerlar ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Adminga xabar yuborish - agar foydalanuvchi admin bo'lmasa
    if user.id != ADMIN_ID:
        await context.bot.send_message(chat_id=ADMIN_ID, text="❗ Botga yangi xabar yuklandi.")

    msg = {
        "user": user.full_name,
        "time": timestamp,
        "type": "text",
        "content": update.message.text,
    }
    save_message(msg)

# Quyidagi handlerlar o'zgarmadi, faqat agar kerak bo'lsa xuddi shunday adminga ogohlantirish qo'shishingiz mumkin.

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    document = update.message.document
    file = await document.get_file()
    filename = safe_filename(document.file_name)
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    await file.download_to_drive(file_path)

    if user.id != ADMIN_ID:
        await context.bot.send_message(chat_id=ADMIN_ID, text="❗ Botga yangi fayl yuklandi.")

    msg = {
        "user": user.full_name,
        "time": timestamp,
        "type": "file",
        "content": f"/downloads/{filename}",
    }
    save_message(msg)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    photo = update.message.photo[-1]
    file = await photo.get_file()
    filename = f"{timestamp.replace(':', '_')}_{user.id}_photo.jpg"
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    await file.download_to_drive(file_path)

    if user.id != ADMIN_ID:
        await context.bot.send_message(chat_id=ADMIN_ID, text="❗ Botga yangi rasm yuklandi.")

    msg = {
        "user": user.full_name,
        "time": timestamp,
        "type": "photo",
        "content": f"/downloads/{filename}",
    }
    save_message(msg)

# Shu tarzda boshqa handlerlarga ham xohlasangiz xabar yuborishni qo'shishingiz mumkin
# Lekin siz faqat text xabarlar uchun desangiz, faqat handle_message ga qo'shish yetarli

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    audio = update.message.audio
    file = await audio.get_file()
    filename = safe_filename(audio.file_name or f"{timestamp}_{user.id}.mp3")
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    await file.download_to_drive(file_path)

    if user.id != ADMIN_ID:
        await context.bot.send_message(chat_id=ADMIN_ID, text="❗ Botga yangi audio yuklandi.")

    msg = {
        "user": user.full_name,
        "time": timestamp,
        "type": "audio",
        "content": f"/downloads/{filename}",
    }
    save_message(msg)

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    video = update.message.video
    file = await video.get_file()
    filename = safe_filename(video.file_name or f"{timestamp}_{user.id}.mp4")
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    await file.download_to_drive(file_path)

    if user.id != ADMIN_ID:
        await context.bot.send_message(chat_id=ADMIN_ID, text="❗ Botga yangi video yuklandi.")

    msg = {
        "user": user.full_name,
        "time": timestamp,
        "type": "video",
        "content": f"/downloads/{filename}",
    }
    save_message(msg)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    voice = update.message.voice
    file = await voice.get_file()
    filename = f"{timestamp.replace(':', '_')}_{user.id}_voice.ogg"
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    await file.download_to_drive(file_path)

    if user.id != ADMIN_ID:
        await context.bot.send_message(chat_id=ADMIN_ID, text="❗ Botga yangi ovozli xabar yuklandi.")

    msg = {
        "user": user.full_name,
        "time": timestamp,
        "type": "voice",
        "content": f"/downloads/{filename}",
    }
    save_message(msg)

async def handle_video_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    video_note = update.message.video_note
    file = await video_note.get_file()
    filename = f"{timestamp.replace(':', '_')}_{user.id}_videonote.mp4"
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    await file.download_to_drive(file_path)

    if user.id != ADMIN_ID:
        await context.bot.send_message(chat_id=ADMIN_ID, text="❗ Botga yangi video note yuklandi.")

    msg = {
        "user": user.full_name,
        "time": timestamp,
        "type": "video_note",
        "content": f"/downloads/{filename}",
    }
    save_message(msg)

if __name__ == "__main__":
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    application = Application.builder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.AUDIO, handle_audio))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.add_handler(MessageHandler(filters.VIDEO_NOTE, handle_video_note))

    print("✅ Telegram bot ishga tushdi...")
    application.run_polling()
