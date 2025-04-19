
import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from flask import Flask, request

BOT_TOKEN = "7691837029:AAEnuEemUNJWI5sTISgeL1CwxR5ahw6MU4A"
PORT = int(os.environ.get("PORT", 8443))
APP_URL = os.environ.get("APP_URL")

ADMINS = [717220095]

app = Flask(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    buttons = [
        [InlineKeyboardButton("Open App", web_app=WebAppInfo(url="https://umiverse.io"))],
        [InlineKeyboardButton("Join Telegram", url="https://t.me/UMIVERSE_Official")],
        [InlineKeyboardButton("White Paper", url="https://gitbook.umiverse.io/umiverse-gitbook")],
        [InlineKeyboardButton("Support", url="https://t.me/UMIVERSE_Official/50379")]
    ]

    if user_id in ADMINS:
        buttons.append([InlineKeyboardButton("Admin Panel", callback_data="admin")])

    await update.message.reply_photo(
        photo="https://www2.0zz0.com/2025/04/19/00/352061437.jpg",
        caption="*Welcome to Umiverse Bot!*\nClick one of the buttons below:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@app.route("/")
def index():
    return "Bot is running!"

async def webhook_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await application.process_update(update)

if __name__ == "__main__":
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=f"{APP_URL}/{BOT_TOKEN}"
    )
