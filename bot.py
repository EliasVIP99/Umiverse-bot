import logging
import sqlite3
from datetime import datetime, date
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from flask import Flask

# إعدادات البوت
BOT_TOKEN = "YOUR_BOT_TOKEN"
APP_URL = "https://your-app-name.onrender.com"
PORT = 8443

# إعداد قاعدة البيانات
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    join_date TEXT,
    country TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS stats (
    button TEXT PRIMARY KEY,
    clicks INTEGER DEFAULT 0
)
""")
conn.commit()

# تعريف المسؤولين
ADMINS = [717220095]  # ID تبعك

# إعداد التطبيق
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# دالة لحفظ المستخدمين
def save_user(user_id):
    today = date.today().isoformat()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, join_date) VALUES (?, ?)", (user_id, today))
    conn.commit()

# دالة لزيادة عدد الضغطات على زر معين
def record_click(button):
    cursor.execute("INSERT OR IGNORE INTO stats (button, clicks) VALUES (?, 0)", (button,))
    cursor.execute("UPDATE stats SET clicks = clicks + 1 WHERE button = ?", (button,))
    conn.commit()

# دالة حساب عدد المستخدمين الجدد
def get_stats():
    total_users = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    today = date.today().isoformat()
    today_users = cursor.execute("SELECT COUNT(*) FROM users WHERE join_date = ?", (today,)).fetchone()[0]
    weekly_users = cursor.execute("SELECT COUNT(*) FROM users WHERE join_date >= date('now', '-7 days')").fetchone()[0]
    clicks = cursor.execute("SELECT button, clicks FROM stats").fetchall()
    return total_users, today_users, weekly_users, clicks

# رسالة الترحيب
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user(user_id)

    buttons = [
        [InlineKeyboardButton("📱 Launch App", url="https://umiverse-dapp.vercel.app/")],
        [InlineKeyboardButton("✈️ Join Telegram Chat", url="https://t.me/UMIVERSE_Official")],
        [InlineKeyboardButton("📖 Whitepaper", url="https://umiverse.gitbook.io/docs")],
        [InlineKeyboardButton("❓ Support", url="https://t.me/UMIVERSE_Official/50379")],
    ]

    if user_id in ADMINS:
        buttons.append([InlineKeyboardButton("🔒 Admin Panel", callback_data="admin")])

    await update.message.reply_photo(
        photo="https://www2.0zz0.com/2025/04/19/00/352061437.jpg",
        caption=(
            """*Welcome to Umiverse!*

"
            "A robust Web3.0 Anime Gaming platform & LaunchPad for Otaku’s by Otaku’s. 💥🗡️"""

"
            "Choose an option below to explore more:"
        ),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# كولباك زر الأدمن
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "admin":
        if user_id in ADMINS:
            total, today, weekly, clicks = get_stats()
            stats_text = (
                f"👥 Total Users: {total}"
"
                f"🆕 Joined Today: {today}"
"
                f"📅 Joined This Week: {weekly}"
"
                "📊 Button Clicks:
"
            )
            for button, count in clicks:
                stats_text += f"- {button}: {count}
"
            await query.edit_message_text(stats_text)
        else:
            await query.edit_message_text("You are not authorized to view this panel.")

# تتبع زر يتم الضغط عليه
async def button_click_tracker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        record_click(update.callback_query.data)

# نقطة البداية
if __name__ == "__main__":
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(CallbackQueryHandler(button_click_tracker, block=False))

    app.route("/")(lambda: "Bot is running!")
    application.run_polling()
