import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from keep_alive import keep_alive  # <--- IMPORT THE FAKE SERVER

# 1. Setup Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 2. YOUR REFERRAL LINKS
BINANCE_LINK = "https://accounts.binance.com/register?ref=YOUR_ID"
BYBIT_LINK = "https://www.bybit.com/register?affiliate_id=YOUR_ID"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🚀 **Crypto Signal Bot Active!**\n\nType `/p bitcoin` to check prices.",
        parse_mode='Markdown'
    )

async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="⚠️ Usage: `/p bitcoin`", parse_mode='Markdown')
            return

        coin_id = context.args[0].lower()
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true"
        response = requests.get(url)
        data = response.json()

        if coin_id in data:
            price = data[coin_id]['usd']
            change = data[coin_id]['usd_24h_change']
            emoji = "🟢 🚀" if change > 0 else "🔴 🔻"
            sign = "+" if change > 0 else ""

            message = (
                f"💎 **{coin_id.upper()} Market Update**\n\n"
                f"💰 **Price:** ${price:,.2f}\n"
                f"📊 **24h Change:** {emoji} {sign}{change:.2f}%\n"
            )

            keyboard = [
                [InlineKeyboardButton("🔥 Trade on Binance", url=BINANCE_LINK)],
                [InlineKeyboardButton("⚡ Trade on Bybit", url=BYBIT_LINK)]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="❌ Coin not found. Try: `/p bitcoin`")

    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == '__main__':
    token = os.getenv("TOKEN")
    
    if not token:
        print("CRITICAL ERROR: Token not found!")
    else:
        keep_alive()  # <--- START THE FAKE SERVER BEFORE THE BOT
        application = ApplicationBuilder().token(token).build()
        application.add_handler(CommandHandler('start', start))
        application.add_handler(CommandHandler('p', get_price))
        application.add_handler(CommandHandler('price', get_price))
        
        print("Crypto Bot Started...")
        application.run_polling()
