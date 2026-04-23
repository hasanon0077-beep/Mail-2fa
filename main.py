import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import pyotp
import requests
import urllib.parse

# ==========================================
# TELEGRAM BOT CONFIGURATION
# ==========================================
# আপনার বটের টোকেন
BOT_TOKEN = "8712557966:AAEuLDVPRyTvLDmsx9uNvGgG7w04sAeeWBo"
API_KEY_DONGVANFB = "36458879248967a36"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode='HTML')

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def main_menu_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton('🔐 2FA Code', callback_data='btn_2fa'),
        InlineKeyboardButton('📧 Hot mail Code', callback_data='btn_hotmail')
    )
    markup.row(
        InlineKeyboardButton('🌐 Temp Mail', url='https://temp-mail.asia/')
    )
    return markup

def get_hotmail_otp(email):
    url = f"https://api.dongvanfb.net/get_messages?apikey={API_KEY_DONGVANFB}&mail={urllib.parse.quote(email)}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        return data.get('code', "Wait... / No Code Found")
    except Exception as e:
        return "Wait... / No Code Found"

# ==========================================
# MAIN BOT LOGIC
# ==========================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id, 
        "<b>👋 স্বাগতম! মেনু থেকে যেকোনো একটি সিলেক্ট করুন:</b>", 
        reply_markup=main_menu_keyboard()
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if call.data == 'btn_2fa':
        msg = bot.edit_message_text(
            "<b>🔐 আপনার 2FA Key (Secret Key) দিন:</b>", 
            chat_id, message_id
        )
        bot.register_next_step_handler(msg, process_2fa_step)

    elif call.data == 'btn_hotmail':
        msg = bot.edit_message_text(
            "<b>📧 আপনার Hotmail Key / Email দিন:</b>", 
            chat_id, message_id
        )
        bot.register_next_step_handler(msg, process_hotmail_step)

    elif call.data == 'btn_back':
        bot.edit_message_text(
            "<b>👋 স্বাগতম! মেনু থেকে যেকোনো একটি সিলেক্ট করুন:</b>", 
            chat_id, message_id, 
            reply_markup=main_menu_keyboard()
        )

    elif call.data.startswith('ref_2fa|'):
        secret = call.data.split('|')[1]
        try:
            totp = pyotp.TOTP(secret.replace(' ', '').upper())
            otp = totp.now()
            
            markup = InlineKeyboardMarkup()
            markup.row(InlineKeyboardButton('🔄 Refresh', callback_data=f'ref_2fa|{secret}'))
            markup.row(InlineKeyboardButton('🔙 Back', callback_data='btn_back'))
            
            bot.edit_message_text(
                f"<b>🔐 2FA Code:</b> <code>{otp}</code>", 
                chat_id, message_id, 
                reply_markup=markup
            )
        except Exception:
            bot.answer_callback_query(call.id, "Invalid Key!")

    elif call.data.startswith('ref_hot|'):
        email = call.data.split('|')[1]
        otp_code = get_hotmail_otp(email)
        
        text = f"<b>📧 Email:</b> <code>{email}</code>\n<b>🔑 OTP:</b> <code>{otp_code}</code>"
        
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton('🔄 Refresh', callback_data=f'ref_hot|{email}'))
        markup.row(InlineKeyboardButton('🔙 Back', callback_data='btn_back'))
        
        bot.edit_message_text(text, chat_id, message_id, reply_markup=markup)

# Next Step Handlers
def process_2fa_step(message):
    secret = message.text.strip()
    try:
        totp = pyotp.TOTP(secret.replace(' ', '').upper())
        otp = totp.now()
        
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton('🔄 Refresh', callback_data=f'ref_2fa|{secret}'))
        markup.row(InlineKeyboardButton('🔙 Back', callback_data='btn_back'))
        
        bot.send_message(message.chat.id, f"<b>🔐 2FA Code:</b> <code>{otp}</code>", reply_markup=markup)
    except Exception:
        bot.send_message(message.chat.id, "❌ ভুল 2FA Key দিয়েছেন। আবার চেষ্টা করুন।")

def process_hotmail_step(message):
    email = message.text.strip().split('|')[0]
    otp_code = get_hotmail_otp(email)
    
    text = f"<b>📧 Email:</b> <code>{email}</code>\n<b>🔑 OTP:</b> <code>{otp_code}</code>"
    
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton('🔄 Refresh', callback_data=f'ref_hot|{email}'))
    markup.row(InlineKeyboardButton('🔙 Back', callback_data='btn_back'))
    
    bot.send_message(message.chat.id, text, reply_markup=markup)

if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()
