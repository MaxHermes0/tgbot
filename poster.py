
from telegram import Bot, Update, InputFile
from telegram.ext import Application, CommandHandler, ContextTypes
from pathlib import Path
import asyncio
import json
import os
import random
import nest_asyncio

BOT_TOKEN = "7940543543:AAHWXa9RdQC-xt-U8TsTnKtmzTYkd-BMaBE"
WEBHOOK_URL = "https://tgbot-o0ze.onrender.com/webhook/7940543543:AAHWXa9RdQC-xt-U8TsTnKtmzTYkd-BMaBE"

IMAGE_PATH = Path("image.jpg")
CAPTION = "Привет"
TEXT_MESSAGES = ["Здравствуйте", "Hello", "Hi there!", "Доброго дня!", "Привет всем!"]
POST_EVERY_SECONDS = 24 * 60 * 60
CHANNELS_FILE = "channels.json"

def load_channels():
    if not Path(CHANNELS_FILE).exists():
        return []
    with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

async def post(application):
    channels = load_channels()
    if not channels:
        print("[info] No channels registered; broadcast skipped")
        return
    if not IMAGE_PATH.exists():
        print("[warn] image.jpg not found – broadcast skipped")
        return
    for channel in channels:
        try:
            await application.bot.send_photo(
                chat_id=channel,
                photo=InputFile(IMAGE_PATH.open("rb"), filename=IMAGE_PATH.name),
                caption=random.choice(TEXT_MESSAGES)
            )
            await asyncio.sleep(1.5)
            print(f"[post] Sent to {channel}")
        except Exception as e:
            print(f"[error] Failed to send to {channel}: {e}")

async def manual_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await post(context.application)
    await update.message.reply_text("Пост отправлен на все каналы.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот работает через Webhook!")

async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("post", manual_post))

    async def scheduled_posting():
        while True:
            await post(app)
            await asyncio.sleep(POST_EVERY_SECONDS)

    asyncio.create_task(scheduled_posting())

    print("[startup] Setting webhook and starting application...")
    await app.bot.set_webhook(url=WEBHOOK_URL)
    await app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(main())
