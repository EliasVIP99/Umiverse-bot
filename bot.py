
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from datetime import datetime, timedelta

BOT_TOKEN = "7691837029:AAEnuEemUNJWI5sTISgeL1CwxR5ahw6MU4A"
ADMIN_IDS = [717220095]
LOGO_URL = "https://www2.0zz0.com/2025/04/19/00/352061437.jpg"

# إعداد قاعدة البيانات
conn = sqlite3.connect("umiverse.db", check_same_thread=False)
c = conn.cursor()
c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        joined_at TEXT
    )
""")
c.execute("""
    CREATE TABLE IF NOT EXISTS actions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT,
        timestamp TEXT
    )
""")
conn.commit()

# تسجيل المستخدم
def log_user(user):
    now = datetime.utcnow().isoformat()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user.id,))
    if not c.fetchone():
        c.execute("INSERT INTO users (user_id, username, first_name, joined_at) VALUES (?, ?, ?, ?)",
                  (user.id, user.username, user.first_name, now))
        conn.commit()

# تسجيل أي ضغطة زر
def log_action(user_id, action):
    now = datetime.utcnow().isoformat()
    c.execute("INSERT INTO actions (user_id, action, timestamp) VALUES (?, ?, ?)",
              (user_id, action, now))
    conn.commit()

# الأمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    log_user(user)
    keyboard = [
        [InlineKeyboardButton("📱 Launch App", web_app=WebAppInfo(url="https://umiverse.io"))],
        [InlineKeyboardButton("✈️ Join Telegram Chat", url="https://t.me/UMIVERSE_Official")],
        [InlineKeyboardButton("📖 Whitepaper", url="https://gitbook.umiverse.io/umiverse-gitbook")],
        [InlineKeyboardButton("❓ Support", url="https://t.me/UMIVERSE_Official/50379")]
    ]
    if user.id in ADMIN_IDS:
        keyboard.append([InlineKeyboardButton("🔐 Admin Panel", callback_data="admin")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_text = (
        "*Welcome to Umiverse!*\n\n"
        "A robust Web3.0 Anime Gaming platform & LaunchPad for Otaku’s by Otaku’s. 📱💥⚔️\n\n"
        "Choose an option below to explore more:"
    )
    await update.message.reply_photo(photo=LOGO_URL, caption=welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

# زر الادمن
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    await query.answer()

    if query.data == "admin" and user.id in ADMIN_IDS:
        c.execute("SELECT COUNT(*) FROM users")
        total_users = c.fetchone()[0]

        today = datetime.utcnow().date()
        week_ago = today - timedelta(days=7)
        c.execute("SELECT COUNT(*) FROM users WHERE DATE(joined_at) = ?", (today.isoformat(),))
        today_count = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM users WHERE DATE(joined_at) >= ?", (week_ago.isoformat(),))
        week_count = c.fetchone()[0]

        actions = {}
        for act in ["launch", "telegram", "whitepaper"]:
            c.execute("SELECT COUNT(*) FROM actions WHERE action = ?", (act,))
            actions[act] = c.fetchone()[0]

        msg = f"🔐 *Admin Panel Stats:*\n\n"
        msg += f"👥 Total users: `{total_users}`\n"
        msg += f"📅 New today: `{today_count}`\n"
        msg += f"📈 New this week: `{week_count}`\n\n"
        msg += f"🔹 Launch App clicks: `{actions['launch']}`\n"
        msg += f"🔹 Telegram clicks: `{actions['telegram']}`\n"
        msg += f"🔹 Whitepaper clicks: `{actions['whitepaper']}`"

        await query.edit_message_text(msg, parse_mode="Markdown")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.run_polling()
