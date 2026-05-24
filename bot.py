import os
import sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("8992089200:AAG5S5LmMQKg_lQG1b0nIkZ_mPT7fqcY-Sc")

conn = sqlite3.connect("bot.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance REAL DEFAULT 0
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS withdrawals (
    user_id INTEGER,
    address TEXT,
    amount REAL
)
""")

conn.commit()

def add_user(user_id):
    cur.execute("INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, ?)", (user_id, 0))
    conn.commit()

def add_balance(user_id, amount):
    add_user(user_id)
    cur.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()

def get_balance(user_id):
    cur.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    result = cur.fetchone()
    return result[0] if result else 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    add_balance(user_id, 0.005)

    await update.message.reply_text(
        "👋 Welcome!\nYou earned $0.005 🎉\nUse /balance"
    )

async def earn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    add_balance(user_id, 0.003)

    await update.message.reply_text("🎉 You earned $0.003")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    bal = get_balance(user_id)

    await update.message.reply_text(f"💰 Balance: ${bal:.3f}")

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if len(context.args) == 0:
        await update.message.reply_text("❌ Send your USDT address: /withdraw address")
        return

    address = context.args[0]
    bal = get_balance(user_id)

    if bal < 1:
        await update.message.reply_text("❌ Minimum withdrawal is $1")
        return

    cur.execute("INSERT INTO withdrawals VALUES (?, ?, ?)", (user_id, address, bal))
    cur.execute("UPDATE users SET balance = 0 WHERE user_id = ?", (user_id,))
    conn.commit()

    await update.message.reply_text("✅ Withdrawal request sent!")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("earn", earn))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("withdraw", withdraw))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
