from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import logging
from app import config

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    当用户发送 /start 命令时，回复一条欢迎消息。
    """
    await update.message.reply_text("Hello! I'm Scantether Bot. I will notify you of new transactions.")

def notify_new_transaction(text: str):
    """
    向配置的 Telegram Chat 发送新交易通知消息。
    这里是同步调用，如果调用方为异步环境，
    可通过线程池或 asyncio.to_thread 将此同步函数封装后再调用。
    """
    bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
    try:
        bot.send_message(chat_id=config.TELEGRAM_CHAT_ID, text=text)
    except Exception as e:
        logging.error("Failed to send Telegram notification: %s", e)

def run_telegram_bot():
    """
    运行 Telegram Bot（采用 Polling 模式），用户可发送 /start 命令与机器人交互。
    """
    application = ApplicationBuilder().token(config.TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.run_polling()

if __name__ == "__main__":
    run_telegram_bot() 