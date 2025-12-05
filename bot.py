import os
import telebot
from telebot import types

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")   # Your Telegram ID

bot = telebot.TeleBot(TOKEN)

# ======================
# STOCK DATA
# ======================
STOCK = {
    "1000": int(os.getenv("STOCK_1000", 0)),
    "2000": int(os.getenv("STOCK_2000", 0)),
    "4000": int(os.getenv("STOCK_4000", 0))
}

PRICES = {
    "1000": 35,
    "2000": 55,
    "4000": 110
}

DISCLAIMER = (
"⚠️ *IMPORTANT DISCLAIMER*\n"
"• Coupons work ONLY on Shein Verse products.\n"
"• Coupons are non-refundable after delivery.\n"
"• Valid till: *31 January 2026*\n"
"• We never send coupons before payment.\n"
"• If payment fails or order gets cancelled, coupon stays valid.\n"
"• Use coupon carefully — misuse can make it invalid.\n"
)


# ======================
# /START — Menu + Disclaimer
# ======================
@bot.message_handler(commands=['start'])
def start(message):
    text = (
        "🎁 *Welcome to Shein Voucher Bot!*\n\n"
        "Please read the disclaimer before using the service ⬇️\n\n"
        f"{DISCLAIMER}\n"
        "Select an option below 👇"
    )

    # Buttons
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🛒 Buy Vouchers", "📦 Available Stock")
    markup.add("📞 Contact Support")

    bot.send_message(
        message.chat.id,
        text,
        parse_mode="Markdown",
        reply_markup=markup
    )


# ======================
# STOCK MESSAGE
# ======================
def send_stock(chat_id):
    msg = (
        "📦 *Current Stock*\n"
        f"• ₹1000: {STOCK['1000']} available\n"
        f"• ₹2000: {STOCK['2000']} available\n"
        f"• ₹4000: {STOCK['4000']} available\n"
    )
    bot.send_message(chat_id, msg, parse_mode="Markdown")


# ======================
# MAIN BOT MENU HANDLER
# ======================
@bot.message_handler(func=lambda message: True)
def menu_handler(message):

    if message.text == "📦 Available Stock":
        send_stock(message.chat.id)

    elif message.text == "🛒 Buy Vouchers":
        markup = types.InlineKeyboardMarkup()
        for amount in STOCK:
            markup.add(
                types.InlineKeyboardButton(
                    f"₹{amount} OFF (₹{PRICES[amount]})",
                    callback_data=f"buy_{amount}"
                )
            )
        bot.send_message(message.chat.id, "Select voucher type:", reply_markup=markup)

    elif message.text == "📞 Contact Support":
        bot.send_message(
            message.chat.id,
            f"📩 *You can contact support here:*\n👉 https://t.me/{ADMIN_ID}",
            parse_mode="Markdown"
        )

    else:
        bot.send_message(message.chat.id, "Please choose an option from menu.")


# ======================
# CALLBACK — USER SELECTED VOUCHER
# ======================
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def buy_voucher(call):
    voucher = call.data.replace("buy_", "")

    if STOCK[voucher] <= 0:
        bot.answer_callback_query(call.id, "Out of stock ❌")
        return

    price = PRICES[voucher]

    pay_link = f"https://yourpaymentgateway.com/pay?amt={price}&user={call.from_user.id}&voucher={voucher}"

    msg = (
        f"🧾 *Voucher Selected:* ₹{voucher}\n"
        f"💰 *Price:* ₹{price}\n\n"
        f"👇 Click below to pay:\n{pay_link}\n\n"
        "_After payment, coupon will be delivered automatically._"
    )

    bot.send_message(call.message.chat.id, msg, parse_mode="Markdown")


# ======================
# MANUAL PAYMENT VERIFICATION (admin)
# ======================
@bot.message_handler(commands=['verify'])
def verify_payment(message):
    try:
        parts = message.text.split()
        user_id = str(parts[1])
        voucher = parts[2]
        coupon = parts[3]

        bot.send_message(user_id, f"🎉 *Your Coupon:* {coupon}", parse_mode="Markdown")
        STOCK[voucher] -= 1
      bot.send_message(message.chat.id, "Delivered successfully ✅")
    except:
        bot.send_message(message.chat.id,
            "Format incorrect ❌\nUse: /verify USERID VOUCHER AMOUNT COUPON"
        )


# ======================
# START BOT
# ======================
bot.infinity_polling()
