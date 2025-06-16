
import os
import json
import random
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

USERS_FILE = "users.json"
REWARDS_FILE = "rewards.json"

def load_data(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return {}

def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_data(USERS_FILE)
    if user_id not in users:
        users[user_id] = {
            "last_open": "2000-01-01",
            "coins": 0,
            "boxes_opened": 0
        }
        save_data(USERS_FILE, users)
    await update.message.reply_text("🎁 Welcome to CryptoSurprise!\nType /open to open your daily box.")
async def open_box(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_data(USERS_FILE)
    rewards = load_data(REWARDS_FILE)
    now = datetime.utcnow()

    last_open = datetime.strptime(users[user_id]["last_open"], "%Y-%m-%d")
    if (now - last_open).days < 1:
        await update.message.reply_text("🕐 You already opened your box today. Come back tomorrow!")
        return

    prize = random.choices(rewards["prizes"], weights=rewards["weights"], k=1)[0]
    users[user_id]["last_open"] = now.strftime("%Y-%m-%d")
    users[user_id]["coins"] += prize["coins"]
    users[user_id]["boxes_opened"] += 1
    save_data(USERS_FILE, users)

    await update.message.reply_text(f"🎉 You got: {prize['text']}
💰 SurpriseCoins: +{prize['coins']}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("open", open_box))
    app.run_polling()

if __name__ == "__main__":
    main()
