import os
import requests
from flask import Flask, request, jsonify
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler
import threading
import asyncio

app = Flask(__name__)
BOT_TOKEN = os.environ.get("8344824887:AAEaVw4dj8A_v_RadPY_pb6U-rNwUAkZFqU")
API_KEY = os.environ.get("YH6iIiq4AFTPT9UgXmvyEOs9amczOL84unCKB5bkjYdOS6qOTO")
DOMAIN = os.environ.get("DOMAIN")

bot = Bot(token=BOT_TOKEN)

@app.route('/payment-status')
def status():
    return "<h1>পেমেন্ট সফল!</h1>"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if data.get("status") == "success":
        user_id = data.get("metadata", {}).get("user_id")
        asyncio.run(bot.send_message(chat_id=user_id, text="✅ পেমেন্ট সফল! ব্যালেন্স অ্যাড করা হয়েছে।"))
    return jsonify({"status": "success"}), 200

async def start(update, context):
    payload = {
        "success_url": f"{DOMAIN}/payment-status",
        "cancel_url": f"{DOMAIN}/payment-status",
        "webhook_url": f"{DOMAIN}/webhook",
        "amount": "50",
        "metadata": {"user_id": str(update.effective_user.id)}
    }
    headers = {'API-KEY': API_KEY, 'Content-Type': 'application/json'}
    res = requests.post("https://secure-pay.nagorikpay.com/api/payment/create", json=payload, headers=headers)
    data = res.json()
    if "payment_url" in data:
        keyboard = [[InlineKeyboardButton("Pay 50 BDT", url=data['payment_url'])]]
        await update.message.reply_text("নিচের বাটনে ক্লিক করে পেমেন্ট করুন:", reply_markup=InlineKeyboardMarkup(keyboard))

def run_bot():
    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.run_polling()

if __name__ == '__main__':
    threading.Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
