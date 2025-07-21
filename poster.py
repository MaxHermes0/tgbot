
from telegram import Bot, InputFile
from telegram.ext import Application, CommandHandler
from pathlib import Path
import asyncio
import json
import random
import os

BOT_TOKEN = "7940543543:AAHWXa9RdQC-xt-U8TsTnKtmzTYkd-BMaBE"

IMAGE_PATH = Path("image.jpg")
CAPTION = "Привет"
TEXT_MESSAGES = ["Здравствуйте", "Hello", "Hi there!", "Доброго дня!", "Привет всем!"]
MESSAGES_PER_CYCLE_RANGE = (3, 4)
POST_EVERY_SECONDS = 24 * 60 * 60

CHANNELS_FILE = "channels.json"

def load_channels():
    if not Path(CHANNELS_FILE).exists():
        return []
    with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_channels(channels):
    with open(CHANNELS_FILE, "w", encoding="utf-8") as f:
        json.dump(channels, f)

async def post(application):
    channels = load_channels()
    if not channels:
        print("[info] No channels registered; broadcast skipped")
        return
    if not IMAGE_PATH.exists():
        print("[warn] image.jpg not found – broadcast skipped")
        return

    text_count = random.randint(*MESSAGES_PER_CYCLE_RANGE)
    texts = random.sample(TEXT_MESSAGES, k=text_count)

    for chat_id in channels:
        try:
            with IMAGE_PATH.open("rb") as image_file:
                await application.bot.send_photo(chat_id=chat_id, photo=image_file, caption=CAPTION)
            for text in texts:
                await application.bot.send_message(chat_id=chat_id, text=text)
        except Exception as e:
            print(f"[error] Failed to post to {chat_id}: {e}")
    print(f"[info] Broadcast complete to {len(channels)} channels")

async def reg(update, context):
    if not context.args:
        return await update.message.reply_text("Укажи @username или ID")
    chat_id = context.args[0]
    channels = load_channels()
    if chat_id not in channels:
        channels.append(chat_id)
        save_channels(channels)
        await update.message.reply_text(f"✅ Добавлен: {chat_id}")
    else:
        await update.message.reply_text(f"⚠️ Уже в списке: {chat_id}")

async def unreg(update, context):
    if not context.args:
        return await update.message.reply_text("Укажи @username или ID")
    chat_id = context.args[0]
    channels = load_channels()
    if chat_id in channels:
        channels.remove(chat_id)
        save_channels(channels)
        await update.message.reply_text(f"🗑 Удалён: {chat_id}")
    else:
        await update.message.reply_text(f"⚠️ Не найден: {chat_id}")

async def list_channels(update, context):
    channels = load_channels()
    if not channels:
        await update.message.reply_text("Список пуст.")
    else:
        await update.message.reply_text("Каналы:\n" + "\n".join(channels))

async def post_command(update, context):
    await post(context.application)

async def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("reg", reg))
    application.add_handler(CommandHandler("unreg", unreg))
    application.add_handler(CommandHandler("list", list_channels))
    application.add_handler(CommandHandler("post", post_command))

    async def scheduled_posting():
        while True:
            await post(application)
            await asyncio.sleep(POST_EVERY_SECONDS)

    asyncio.create_task(scheduled_posting())
    print("[startup] Running bot...")
    await application.run_polling()

import asyncio
import nest_asyncio

if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(main())
