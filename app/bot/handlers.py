from typing import List
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)

from ..config import TELEGRAM_BOT_TOKEN
from ..database.operations import db_manager
from ..utils.helpers import validate_tron_address
from ..utils.logger import setup_logger
from . import messages
from ..utils.retry import async_retry
from telegram.error import TelegramError

logger = setup_logger('bot.handlers')

class TronBot:
    def __init__(self):
        # 添加错误处理
        if not TELEGRAM_BOT_TOKEN:
            raise ValueError("Bot token not set")
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self._setup_handlers()

    def _setup_handlers(self):
        """设置命令处理器"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("add", self.add_address))
        self.application.add_handler(CommandHandler("remove", self.remove_address))
        self.application.add_handler(CommandHandler("list", self.list_addresses))
        self.application.add_handler(CommandHandler("txs", self.get_transactions))
        
        # 添加错误处理器
        self.application.add_error_handler(self.error_handler)

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /start 命令"""
        await update.message.reply_text(
            messages.START_MESSAGE,
            parse_mode='Markdown'
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /help 命令"""
        await update.message.reply_text(
            messages.HELP_MESSAGE,
            parse_mode='Markdown'
        )

    async def add_address(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /add 命令"""
        if not context.args:
            await update.message.reply_text("请提供要监控的地址！\n示例：/add <地址> [备注]")
            return

        address = context.args[0]
        note = " ".join(context.args[1:]) if len(context.args) > 1 else None

        if not validate_tron_address(address):
            await update.message.reply_text(messages.INVALID_ADDRESS)
            return

        try:
            success = await db_manager.add_address(
                address=address,
                chat_id=update.effective_chat.id,
                note=note
            )
            
            if success:
                await update.message.reply_text(
                    messages.ADDRESS_ADDED.format(address, note or "无"),
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(messages.ADDRESS_ALREADY_EXISTS)
        except Exception as e:
            logger.error(f"Error adding address: {str(e)}")
            await update.message.reply_text(messages.GENERAL_ERROR)

    async def remove_address(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /remove 命令"""
        if not context.args:
            await update.message.reply_text("请提供要移除的地址！")
            return

        address = context.args[0]
        try:
            success = await db_manager.remove_address(
                address=address,
                chat_id=update.effective_chat.id
            )
            
            if success:
                await update.message.reply_text(
                    messages.ADDRESS_REMOVED.format(address),
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(messages.ADDRESS_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error removing address: {str(e)}")
            await update.message.reply_text(messages.GENERAL_ERROR)

    async def list_addresses(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /list 命令"""
        try:
            addresses = await db_manager.get_active_addresses()
            message = messages.format_address_list([
                {"address": addr.address, "note": addr.note}
                for addr in addresses
            ])
            await update.message.reply_text(message, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error listing addresses: {str(e)}")
            await update.message.reply_text(messages.GENERAL_ERROR)

    async def get_transactions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /txs 命令"""
        if not context.args:
            await update.message.reply_text("请提供要查询的地址！")
            return

        address = context.args[0]
        try:
            txs = await db_manager.get_address_transactions(address, limit=5)
            message = messages.format_transaction_list(txs, address)
            await update.message.reply_text(message, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error getting transactions: {str(e)}")
            await update.message.reply_text(messages.GENERAL_ERROR)

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理错误"""
        logger.error(f"Update {update} caused error {context.error}")
        try:
            if update and update.effective_message:
                await update.effective_message.reply_text(messages.GENERAL_ERROR)
        except Exception as e:
            logger.error(f"Error in error handler: {str(e)}")

    def run(self):
        """运行机器人"""
        self.application.run_polling()

    # 添加优雅关闭方法
    async def shutdown(self):
        await self.application.shutdown()

    @async_retry(
        retries=2,
        delay=1.0,
        exceptions=(TelegramError,),
        on_retry=lambda attempt, error, *args, **kwargs: logger.warning(f"Telegram API error: {error}")
    )
    async def send_transaction_alert(self, chat_id: int, message: str):
        await self.application.bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode='Markdown'
        )

# 创建bot实例
bot = TronBot() 